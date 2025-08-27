import math
from pathlib import Path
from typing import List, Optional

import gpxpy
from haversine import haversine, Unit

from .course import Course, CoursePoint, CourseSegment


class GPXParser:
    """Parse GPX files and convert to Course objects"""
    
    def __init__(self, min_segment_distance_m: float = 10.0):
        """
        Initialize GPX parser
        
        Args:
            min_segment_distance_m: Minimum distance between points to create a segment
        """
        self.min_segment_distance_m = min_segment_distance_m
    
    def parse_gpx_file(self, file_path: Path, course_name: Optional[str] = None) -> Course:
        """
        Parse GPX file and return Course object
        
        Args:
            file_path: Path to GPX file
            course_name: Optional course name, defaults to filename
            
        Returns:
            Course object with parsed data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"GPX file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            gpx_data = gpxpy.parse(f)
        
        if not gpx_data.tracks:
            raise ValueError("No tracks found in GPX file")
        
        # Use first track
        track = gpx_data.tracks[0]
        
        # Extract all points from all segments
        all_points = []
        for segment in track.segments:
            all_points.extend(segment.points)
        
        if len(all_points) < 2:
            raise ValueError("GPX file must contain at least 2 points")
        
        # Convert to CoursePoints
        course_points = self._convert_to_course_points(all_points)
        
        # Create segments
        segments = self._create_segments(course_points)
        
        # Calculate course metadata
        name = course_name or file_path.stem
        total_distance_km = course_points[-1].distance_km
        total_elevation_gain, total_elevation_loss = self._calculate_elevation_totals(segments)
        
        return Course(
            name=name,
            segments=segments,
            total_distance_km=total_distance_km,
            total_elevation_gain_m=total_elevation_gain,
            total_elevation_loss_m=total_elevation_loss,
            start_elevation_m=course_points[0].elevation_m,
            end_elevation_m=course_points[-1].elevation_m,
            max_gradient_percent=max(seg.gradient_percent for seg in segments),
            min_gradient_percent=min(seg.gradient_percent for seg in segments)
        )
    
    def _convert_to_course_points(self, gpx_points: List) -> List[CoursePoint]:
        """Convert GPX points to CoursePoint objects with distances"""
        course_points = []
        cumulative_distance_km = 0.0
        
        for i, point in enumerate(gpx_points):
            # Calculate distance from previous point
            if i > 0:
                prev_point = gpx_points[i - 1]
                distance_km = haversine(
                    (prev_point.latitude, prev_point.longitude),
                    (point.latitude, point.longitude),
                    unit=Unit.KILOMETERS
                )
                cumulative_distance_km += distance_km
            
            course_point = CoursePoint(
                latitude=point.latitude,
                longitude=point.longitude,
                elevation_m=point.elevation or 0.0,  # Handle None elevations
                distance_km=cumulative_distance_km
            )
            
            course_points.append(course_point)
        
        return course_points
    
    def _create_segments(self, course_points: List[CoursePoint]) -> List[CourseSegment]:
        """Create course segments from points, filtering by minimum distance"""
        segments = []
        
        for i in range(len(course_points) - 1):
            start_point = course_points[i]
            end_point = course_points[i + 1]
            
            # Calculate segment properties
            distance_m = self._calculate_distance_meters(start_point, end_point)
            
            # Skip segments that are too short
            if distance_m < self.min_segment_distance_m:
                continue
            
            elevation_gain_m = end_point.elevation_m - start_point.elevation_m
            gradient_percent = self._calculate_gradient(elevation_gain_m, distance_m)
            bearing_degrees = self._calculate_bearing(start_point, end_point)
            
            segment = CourseSegment(
                start_point=start_point,
                end_point=end_point,
                distance_m=distance_m,
                elevation_gain_m=elevation_gain_m,
                gradient_percent=gradient_percent,
                bearing_degrees=bearing_degrees
            )
            
            segments.append(segment)
        
        return segments
    
    def _calculate_distance_meters(self, point1: CoursePoint, point2: CoursePoint) -> float:
        """Calculate distance between two points in meters"""
        return haversine(
            (point1.latitude, point1.longitude),
            (point2.latitude, point2.longitude),
            unit=Unit.METERS
        )
    
    def _calculate_gradient(self, elevation_gain_m: float, distance_m: float) -> float:
        """Calculate gradient as percentage"""
        if distance_m == 0:
            return 0.0
        return (elevation_gain_m / distance_m) * 100
    
    def _calculate_bearing(self, point1: CoursePoint, point2: CoursePoint) -> float:
        """
        Calculate bearing from point1 to point2 in degrees (0-360)
        0 degrees = North, 90 degrees = East
        """
        lat1 = math.radians(point1.latitude)
        lat2 = math.radians(point2.latitude)
        lon_diff = math.radians(point2.longitude - point1.longitude)
        
        y = math.sin(lon_diff) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) - 
             math.sin(lat1) * math.cos(lat2) * math.cos(lon_diff))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Convert to 0-360 degrees
        return (bearing_deg + 360) % 360
    
    def _calculate_elevation_totals(self, segments: List[CourseSegment]) -> tuple[float, float]:
        """Calculate total elevation gain and loss"""
        total_gain = sum(seg.elevation_gain_m for seg in segments if seg.elevation_gain_m > 0)
        total_loss = sum(abs(seg.elevation_gain_m) for seg in segments if seg.elevation_gain_m < 0)
        
        return total_gain, total_loss
    
    @staticmethod
    def create_sample_course() -> Course:
        """Create a sample course for testing"""
        # Sample points for a small loop course
        points = [
            CoursePoint(latitude=40.7589, longitude=-73.9851, elevation_m=10.0, distance_km=0.0),
            CoursePoint(latitude=40.7599, longitude=-73.9851, elevation_m=15.0, distance_km=0.1),
            CoursePoint(latitude=40.7609, longitude=-73.9841, elevation_m=25.0, distance_km=0.3),
            CoursePoint(latitude=40.7609, longitude=-73.9831, elevation_m=30.0, distance_km=0.4),
            CoursePoint(latitude=40.7599, longitude=-73.9831, elevation_m=20.0, distance_km=0.5),
            CoursePoint(latitude=40.7589, longitude=-73.9841, elevation_m=12.0, distance_km=0.7),
            CoursePoint(latitude=40.7589, longitude=-73.9851, elevation_m=10.0, distance_km=0.8)
        ]
        
        # Create segments
        parser = GPXParser()
        segments = parser._create_segments(points)
        
        return Course(
            name="Sample Loop Course",
            segments=segments,
            total_distance_km=0.8,
            total_elevation_gain_m=20.0,
            total_elevation_loss_m=18.0,
            start_elevation_m=10.0,
            end_elevation_m=10.0,
            max_gradient_percent=max(seg.gradient_percent for seg in segments),
            min_gradient_percent=min(seg.gradient_percent for seg in segments)
        )