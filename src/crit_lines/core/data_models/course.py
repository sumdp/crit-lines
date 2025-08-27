from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class CoursePoint(BaseModel):
    """Single point on a course with position and elevation"""
    
    latitude: float = Field(description="Latitude in decimal degrees")
    longitude: float = Field(description="Longitude in decimal degrees") 
    elevation_m: float = Field(description="Elevation in meters")
    distance_km: float = Field(ge=0, description="Cumulative distance from start in kilometers")


class CourseSegment(BaseModel):
    """Segment of course between two points with calculated properties"""
    
    start_point: CoursePoint = Field(description="Segment start point")
    end_point: CoursePoint = Field(description="Segment end point")
    
    # Calculated properties
    distance_m: float = Field(ge=0, description="Segment distance in meters")
    elevation_gain_m: float = Field(description="Elevation gain in meters (negative for descent)")
    gradient_percent: float = Field(description="Average gradient as percentage")
    bearing_degrees: Optional[float] = Field(default=None, description="Bearing in degrees (0-360)")

    @property 
    def is_climb(self) -> bool:
        """Check if segment is a climb (positive gradient)"""
        return self.gradient_percent > 0
    
    @property
    def is_descent(self) -> bool:
        """Check if segment is a descent (negative gradient)"""
        return self.gradient_percent < 0
    
    @property
    def is_flat(self) -> bool:
        """Check if segment is flat (gradient within ±0.5%)"""
        return abs(self.gradient_percent) <= 0.5


class Course(BaseModel):
    """Complete course with segments and metadata"""
    
    name: str = Field(description="Course name")
    segments: List[CourseSegment] = Field(description="Course segments")
    
    # Metadata
    total_distance_km: float = Field(ge=0, description="Total course distance in kilometers")
    total_elevation_gain_m: float = Field(ge=0, description="Total elevation gain in meters") 
    total_elevation_loss_m: float = Field(ge=0, description="Total elevation loss in meters")
    start_elevation_m: float = Field(description="Starting elevation in meters")
    end_elevation_m: float = Field(description="Ending elevation in meters")
    
    # Course classification
    max_gradient_percent: float = Field(description="Maximum gradient on course")
    min_gradient_percent: float = Field(description="Minimum gradient on course (most negative)")
    
    @property
    def net_elevation_gain_m(self) -> float:
        """Calculate net elevation change"""
        return self.end_elevation_m - self.start_elevation_m
    
    @property
    def elevation_factor(self) -> float:
        """Calculate elevation factor (total gain / distance)"""
        if self.total_distance_km == 0:
            return 0
        return self.total_elevation_gain_m / (self.total_distance_km * 1000)
    
    @property
    def course_difficulty_score(self) -> float:
        """Simple difficulty score based on distance and elevation"""
        # Fiets score approximation: distance_km + (elevation_gain_m / 10)
        return self.total_distance_km + (self.total_elevation_gain_m / 10)
    
    def get_climbing_segments(self, min_gradient: float = 2.0) -> List[CourseSegment]:
        """Get segments that are climbs above threshold gradient"""
        return [seg for seg in self.segments if seg.gradient_percent >= min_gradient]
    
    def get_descent_segments(self, max_gradient: float = -2.0) -> List[CourseSegment]:
        """Get segments that are descents below threshold gradient"""
        return [seg for seg in self.segments if seg.gradient_percent <= max_gradient]
    
    def get_flat_segments(self, gradient_tolerance: float = 2.0) -> List[CourseSegment]:
        """Get segments that are relatively flat"""
        return [seg for seg in self.segments 
                if abs(seg.gradient_percent) < gradient_tolerance]


class WindConditions(BaseModel):
    """Wind conditions for simulation"""
    
    speed_kmh: float = Field(ge=0, description="Wind speed in km/h")
    direction_degrees: float = Field(ge=0, lt=360, description="Wind direction in degrees (0-360)")
    
    @property
    def speed_ms(self) -> float:
        """Wind speed in meters per second"""
        return self.speed_kmh / 3.6


class CourseConditions(BaseModel):
    """Environmental conditions for course simulation"""
    
    temperature_c: float = Field(description="Temperature in Celsius")
    humidity_percent: float = Field(ge=0, le=100, description="Humidity percentage")
    pressure_hpa: float = Field(default=1013.25, description="Air pressure in hPa")
    wind: Optional[WindConditions] = Field(default=None, description="Wind conditions")
    
    @property
    def air_density_kg_m3(self) -> float:
        """Calculate air density based on temperature, humidity, and pressure"""
        # Simplified air density calculation
        # More accurate calculation would use actual humidity effects
        temp_kelvin = self.temperature_c + 273.15
        return (self.pressure_hpa * 100) / (287.05 * temp_kelvin)