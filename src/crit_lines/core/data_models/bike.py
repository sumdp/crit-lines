from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BikeType(str, Enum):
    """Bike type affects weight and aerodynamics"""
    ROAD = "road"
    AERO = "aero"
    CLIMBING = "climbing"
    TT = "time_trial"
    GRAVEL = "gravel"


class WheelType(str, Enum):
    """Wheel type affects aerodynamics and weight"""
    STANDARD = "standard"
    AERO_SHALLOW = "aero_shallow"  # 30-50mm
    AERO_DEEP = "aero_deep"       # 50-80mm
    DISC = "disc"
    CLIMBING = "climbing"          # Lightweight


class Bike(BaseModel):
    """Bicycle equipment characteristics"""
    
    # Basic properties
    bike_type: BikeType = Field(default=BikeType.ROAD, description="Type of bicycle")
    weight_kg: float = Field(gt=0, description="Bike weight in kilograms")
    
    # Wheels
    wheel_type: WheelType = Field(default=WheelType.STANDARD, description="Wheel type")
    wheel_weight_kg: Optional[float] = Field(default=None, gt=0, description="Wheelset weight in kg")
    
    # Aerodynamics
    frame_cda_m2: Optional[float] = Field(
        default=None,
        gt=0,
        description="Frame coefficient of drag × area (m²). If None, calculated from bike_type"
    )
    wheel_cda_m2: Optional[float] = Field(
        default=None,
        gt=0, 
        description="Wheel coefficient of drag × area (m²). If None, calculated from wheel_type"
    )

    # Rolling resistance  
    crr: float = Field(
        default=0.004,
        gt=0,
        le=0.020,
        description="Coefficient of rolling resistance (typical: 0.003-0.008)"
    )

    @property
    def total_weight_kg(self) -> float:
        """Calculate total bike weight including wheels"""
        wheel_weight = self.wheel_weight_kg or self._default_wheel_weight()
        return self.weight_kg + wheel_weight
    
    @property
    def frame_drag_area(self) -> float:
        """Calculate frame drag area"""
        if self.frame_cda_m2 is not None:
            return self.frame_cda_m2
            
        # Standard frame CdA values by bike type (m²)
        frame_cda = {
            BikeType.ROAD: 0.15,
            BikeType.AERO: 0.12,
            BikeType.CLIMBING: 0.16,
            BikeType.TT: 0.08,
            BikeType.GRAVEL: 0.17
        }
        return frame_cda[self.bike_type]
    
    @property
    def wheel_drag_area(self) -> float:
        """Calculate wheel drag area"""
        if self.wheel_cda_m2 is not None:
            return self.wheel_cda_m2
            
        # Standard wheel CdA values by wheel type (m²)
        wheel_cda = {
            WheelType.STANDARD: 0.10,
            WheelType.AERO_SHALLOW: 0.08,
            WheelType.AERO_DEEP: 0.06,
            WheelType.DISC: 0.04,
            WheelType.CLIMBING: 0.11
        }
        return wheel_cda[self.wheel_type]
    
    @property
    def total_bike_cda(self) -> float:
        """Calculate total bike drag area (frame + wheels)"""
        return self.frame_drag_area + self.wheel_drag_area

    def _default_wheel_weight(self) -> float:
        """Default wheel weights by type (kg)"""
        wheel_weights = {
            WheelType.STANDARD: 1.8,
            WheelType.AERO_SHALLOW: 1.9,
            WheelType.AERO_DEEP: 2.1,
            WheelType.DISC: 2.3,
            WheelType.CLIMBING: 1.4
        }
        return wheel_weights[self.wheel_type]


class BikeConfig(BaseModel):
    """Configuration for bike comparison scenarios"""
    
    name: str = Field(description="Scenario name")
    bike: Bike = Field(description="Bike configuration")