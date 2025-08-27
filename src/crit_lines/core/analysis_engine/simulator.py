from typing import List, Dict, Any
from dataclasses import dataclass

from ..data_models.bike import Bike, BikeConfig
from ..data_models.course import Course, CourseConditions
from ..data_models.rider import Rider, RiderConfig
from .physics import CyclingPhysics


@dataclass
class SegmentResult:
    """Results for a single course segment"""
    segment_index: int
    distance_m: float
    elevation_gain_m: float
    gradient_percent: float
    time_seconds: float
    average_speed_kmh: float
    power_watts: float


@dataclass
class SimulationResult:
    """Complete simulation results for a course"""
    scenario_name: str
    rider_config: RiderConfig
    bike_config: BikeConfig
    
    # Overall results
    total_time_seconds: float
    total_distance_km: float
    average_speed_kmh: float
    average_power_watts: float
    
    # Segment-by-segment results
    segment_results: List[SegmentResult]
    
    @property
    def total_time_formatted(self) -> str:
        """Format total time as HH:MM:SS"""
        hours = int(self.total_time_seconds // 3600)
        minutes = int((self.total_time_seconds % 3600) // 60)
        seconds = int(self.total_time_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class CourseSimulator:
    """Main simulation engine for course performance analysis"""
    
    def __init__(self):
        self.physics = CyclingPhysics()
    
    def simulate_course(
        self,
        course: Course,
        rider_config: RiderConfig,
        bike_config: BikeConfig,
        conditions: CourseConditions,
        scenario_name: str = "Simulation"
    ) -> SimulationResult:
        """
        Simulate complete course performance
        
        Args:
            course: Course to simulate
            rider_config: Rider configuration
            bike_config: Bike configuration
            conditions: Environmental conditions
            scenario_name: Name for this simulation scenario
            
        Returns:
            Complete simulation results
        """
        segment_results = []
        total_time = 0.0
        total_power_time = 0.0  # For weighted average power
        
        rider = rider_config.rider
        bike = bike_config.bike
        available_power = rider_config.effective_power_watts
        
        for i, segment in enumerate(course.segments):
            # Estimate wind component for this segment
            wind_speed_ms = 0.0
            if conditions.wind and segment.bearing_degrees is not None:
                wind_speed_ms = self.physics.estimate_wind_component(
                    segment, conditions.wind, segment.bearing_degrees
                )
            
            # Calculate time and speed for segment
            time_seconds, speed_ms = self.physics.calculate_time_for_segment(
                rider, bike, segment, available_power, conditions, wind_speed_ms
            )
            
            # Create segment result
            segment_result = SegmentResult(
                segment_index=i,
                distance_m=segment.distance_m,
                elevation_gain_m=segment.elevation_gain_m,
                gradient_percent=segment.gradient_percent,
                time_seconds=time_seconds,
                average_speed_kmh=speed_ms * 3.6,  # Convert to km/h
                power_watts=available_power
            )
            
            segment_results.append(segment_result)
            total_time += time_seconds
            total_power_time += available_power * time_seconds
        
        # Calculate overall metrics
        average_speed_kmh = (course.total_distance_km * 3600) / total_time
        average_power_watts = total_power_time / total_time if total_time > 0 else 0
        
        return SimulationResult(
            scenario_name=scenario_name,
            rider_config=rider_config,
            bike_config=bike_config,
            total_time_seconds=total_time,
            total_distance_km=course.total_distance_km,
            average_speed_kmh=average_speed_kmh,
            average_power_watts=average_power_watts,
            segment_results=segment_results
        )
    
    def compare_scenarios(
        self,
        course: Course,
        scenarios: List[Dict[str, Any]],
        conditions: CourseConditions
    ) -> List[SimulationResult]:
        """
        Compare multiple rider/bike scenarios on the same course
        
        Args:
            course: Course to simulate
            scenarios: List of scenario configurations, each containing:
                - name: Scenario name
                - rider_config: RiderConfig
                - bike_config: BikeConfig
            conditions: Environmental conditions
            
        Returns:
            List of simulation results for comparison
        """
        results = []
        
        for scenario in scenarios:
            result = self.simulate_course(
                course=course,
                rider_config=scenario["rider_config"],
                bike_config=scenario["bike_config"],
                conditions=conditions,
                scenario_name=scenario["name"]
            )
            results.append(result)
        
        # Sort by total time (fastest first)
        results.sort(key=lambda r: r.total_time_seconds)
        
        return results
    
    def analyze_power_impact(
        self,
        course: Course,
        base_rider_config: RiderConfig,
        bike_config: BikeConfig,
        conditions: CourseConditions,
        power_variations: List[float]
    ) -> List[SimulationResult]:
        """
        Analyze impact of different power levels on course performance
        
        Args:
            course: Course to simulate
            base_rider_config: Base rider configuration
            bike_config: Bike configuration
            conditions: Environmental conditions
            power_variations: List of FTP values to test
            
        Returns:
            List of simulation results for different power levels
        """
        results = []
        
        for ftp_watts in power_variations:
            # Create modified rider config
            modified_rider = base_rider_config.rider.model_copy()
            modified_rider.ftp_watts = ftp_watts
            
            modified_config = RiderConfig(
                name=f"FTP_{ftp_watts}W",
                rider=modified_rider,
                effort_percentage=base_rider_config.effort_percentage
            )
            
            result = self.simulate_course(
                course=course,
                rider_config=modified_config,
                bike_config=bike_config,
                conditions=conditions,
                scenario_name=f"FTP {ftp_watts}W"
            )
            
            results.append(result)
        
        return results
    
    def analyze_weight_impact(
        self,
        course: Course,
        base_rider_config: RiderConfig,
        bike_config: BikeConfig,
        conditions: CourseConditions,
        weight_variations: List[float]
    ) -> List[SimulationResult]:
        """
        Analyze impact of different rider weights on course performance
        
        Args:
            course: Course to simulate
            base_rider_config: Base rider configuration  
            bike_config: Bike configuration
            conditions: Environmental conditions
            weight_variations: List of weights in kg to test
            
        Returns:
            List of simulation results for different weights
        """
        results = []
        
        for weight_kg in weight_variations:
            # Create modified rider config
            modified_rider = base_rider_config.rider.model_copy()
            modified_rider.weight_kg = weight_kg
            
            modified_config = RiderConfig(
                name=f"Weight_{weight_kg}kg",
                rider=modified_rider,
                effort_percentage=base_rider_config.effort_percentage
            )
            
            result = self.simulate_course(
                course=course,
                rider_config=modified_config,
                bike_config=bike_config,
                conditions=conditions,
                scenario_name=f"Weight {weight_kg}kg"
            )
            
            results.append(result)
        
        return results