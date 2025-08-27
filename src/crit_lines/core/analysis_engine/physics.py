import math
from typing import Tuple

from ..data_models.bike import Bike
from ..data_models.course import CourseSegment, CourseConditions
from ..data_models.rider import Rider


class CyclingPhysics:
    """Core physics calculations for cycling performance simulation"""
    
    # Physical constants
    GRAVITY = 9.81  # m/s²
    AIR_DENSITY_STD = 1.225  # kg/m³ at sea level, 15°C
    
    def __init__(self):
        pass
    
    def calculate_power_required(
        self,
        rider: Rider,
        bike: Bike,
        segment: CourseSegment,
        speed_ms: float,
        conditions: CourseConditions,
        wind_speed_ms: float = 0.0
    ) -> float:
        """
        Calculate total power required to maintain speed on segment
        
        Args:
            rider: Rider configuration
            bike: Bike configuration  
            segment: Course segment
            speed_ms: Speed in meters per second
            conditions: Environmental conditions
            wind_speed_ms: Headwind component in m/s (positive = headwind)
            
        Returns:
            Required power in watts
        """
        # Total mass (rider + bike)
        total_mass_kg = rider.weight_kg + bike.total_weight_kg
        
        # Power components
        aero_power = self._aerodynamic_power(
            rider, bike, speed_ms, conditions, wind_speed_ms
        )
        
        rolling_power = self._rolling_resistance_power(
            total_mass_kg, bike.crr, speed_ms
        )
        
        gravity_power = self._gravitational_power(
            total_mass_kg, segment.gradient_percent, speed_ms
        )
        
        # Total power (ignoring mechanical losses for simplicity)
        total_power = aero_power + rolling_power + gravity_power
        
        return max(0, total_power)  # Power can't be negative
    
    def calculate_speed_from_power(
        self,
        rider: Rider,
        bike: Bike,
        segment: CourseSegment,
        power_watts: float,
        conditions: CourseConditions,
        wind_speed_ms: float = 0.0,
        tolerance: float = 0.1
    ) -> float:
        """
        Calculate speed given power using iterative method
        
        Args:
            rider: Rider configuration
            bike: Bike configuration
            segment: Course segment
            power_watts: Available power in watts
            conditions: Environmental conditions
            wind_speed_ms: Headwind component in m/s
            tolerance: Speed tolerance for convergence (m/s)
            
        Returns:
            Speed in meters per second
        """
        # Initial guess (rough estimate)
        speed_guess = 10.0  # m/s (~36 km/h)
        
        # Newton-Raphson method for finding speed
        for _ in range(50):  # Max iterations
            power_required = self.calculate_power_required(
                rider, bike, segment, speed_guess, conditions, wind_speed_ms
            )
            
            power_diff = power_required - power_watts
            
            if abs(power_diff) < 1.0:  # Within 1 watt
                break
                
            # Calculate derivative (change in power for small speed change)
            delta_speed = 0.01  # m/s
            power_at_delta = self.calculate_power_required(
                rider, bike, segment, speed_guess + delta_speed, conditions, wind_speed_ms
            )
            
            derivative = (power_at_delta - power_required) / delta_speed
            
            if abs(derivative) < 0.001:  # Avoid division by zero
                break
                
            # Newton-Raphson update
            speed_guess = speed_guess - (power_diff / derivative)
            speed_guess = max(0.1, speed_guess)  # Minimum realistic speed
            
        return speed_guess
    
    def calculate_time_for_segment(
        self,
        rider: Rider,
        bike: Bike,
        segment: CourseSegment,
        power_watts: float,
        conditions: CourseConditions,
        wind_speed_ms: float = 0.0
    ) -> Tuple[float, float]:
        """
        Calculate time and average speed for a segment
        
        Returns:
            Tuple of (time_seconds, average_speed_ms)
        """
        speed_ms = self.calculate_speed_from_power(
            rider, bike, segment, power_watts, conditions, wind_speed_ms
        )
        
        time_seconds = segment.distance_m / speed_ms
        
        return time_seconds, speed_ms
    
    def _aerodynamic_power(
        self,
        rider: Rider,
        bike: Bike,
        speed_ms: float,
        conditions: CourseConditions,
        wind_speed_ms: float
    ) -> float:
        """Calculate power required to overcome aerodynamic drag"""
        # Effective wind speed (bike speed + headwind)
        effective_wind_speed = speed_ms + wind_speed_ms
        
        # Total drag area (rider + bike)
        total_cda = rider.effective_cda + bike.total_bike_cda
        
        # Air density
        air_density = conditions.air_density_kg_m3
        
        # Aerodynamic drag force: F = 0.5 * ρ * CdA * v²
        drag_force = 0.5 * air_density * total_cda * (effective_wind_speed ** 2)
        
        # Power = Force × speed
        return drag_force * speed_ms
    
    def _rolling_resistance_power(
        self,
        total_mass_kg: float,
        crr: float,
        speed_ms: float
    ) -> float:
        """Calculate power required to overcome rolling resistance"""
        # Rolling resistance force: F = Crr × m × g
        rolling_force = crr * total_mass_kg * self.GRAVITY
        
        # Power = Force × speed
        return rolling_force * speed_ms
    
    def _gravitational_power(
        self,
        total_mass_kg: float,
        gradient_percent: float,
        speed_ms: float
    ) -> float:
        """Calculate power required to overcome gravity on inclines"""
        # Convert gradient percentage to angle
        gradient_radians = math.atan(gradient_percent / 100)
        
        # Gravitational force component along slope: F = m × g × sin(θ)
        gravity_force = total_mass_kg * self.GRAVITY * math.sin(gradient_radians)
        
        # Power = Force × speed
        return gravity_force * speed_ms
    
    def estimate_wind_component(
        self,
        segment: CourseSegment,
        wind_conditions,
        course_bearing_degrees: float
    ) -> float:
        """
        Estimate headwind/tailwind component for segment
        
        Args:
            segment: Course segment
            wind_conditions: Wind conditions
            course_bearing_degrees: Direction of travel in degrees
            
        Returns:
            Wind speed component in m/s (positive = headwind, negative = tailwind)
        """
        if wind_conditions is None:
            return 0.0
            
        # Angle difference between wind direction and course bearing
        angle_diff = abs(wind_conditions.direction_degrees - course_bearing_degrees)
        angle_diff = min(angle_diff, 360 - angle_diff)  # Use smaller angle
        
        # Component of wind in direction of travel
        wind_component = wind_conditions.speed_ms * math.cos(math.radians(angle_diff))
        
        # Positive for headwind, negative for tailwind
        if angle_diff > 90:
            wind_component = -wind_component
            
        return wind_component