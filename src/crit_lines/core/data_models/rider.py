from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RidingPosition(str, Enum):
    """Riding position affects aerodynamics"""
    DROPS = "drops"
    HOODS = "hoods"
    TOPS = "tops"
    AERO_BARS = "aero_bars"


class Rider(BaseModel):
    """Rider physical and performance characteristics"""
    
    # Physical attributes
    weight_kg: float = Field(gt=0, description="Rider weight in kilograms")
    height_cm: Optional[float] = Field(default=None, gt=0, description="Rider height in centimeters")
    
    # Performance metrics
    ftp_watts: float = Field(gt=0, description="Functional Threshold Power in watts")
    
    # Aerodynamics
    position: RidingPosition = Field(default=RidingPosition.HOODS, description="Primary riding position")
    cda_m2: Optional[float] = Field(
        default=None, 
        gt=0, 
        description="Coefficient of drag × frontal area (m²). If None, calculated from position"
    )
    
    # Equipment
    clothing_drag_multiplier: float = Field(
        default=1.0, 
        ge=0.8, 
        le=1.3, 
        description="Clothing drag multiplier (0.8=skinsuit, 1.0=normal, 1.3=baggy)"
    )

    @property
    def effective_cda(self) -> float:
        """Calculate effective CdA based on position and clothing"""
        if self.cda_m2 is not None:
            base_cda = self.cda_m2
        else:
            # Standard CdA values by position (m²)
            position_cda = {
                RidingPosition.DROPS: 0.30,
                RidingPosition.HOODS: 0.35, 
                RidingPosition.TOPS: 0.40,
                RidingPosition.AERO_BARS: 0.25
            }
            base_cda = position_cda[self.position]
        
        return base_cda * self.clothing_drag_multiplier
    
    @property
    def power_to_weight_ratio(self) -> float:
        """Calculate power-to-weight ratio in watts/kg"""
        return self.ftp_watts / self.weight_kg


class RiderConfig(BaseModel):
    """Configuration for rider comparison scenarios"""
    
    name: str = Field(description="Scenario name")
    rider: Rider = Field(description="Rider configuration")
    effort_percentage: float = Field(
        default=1.0,
        ge=0.5,
        le=1.2,
        description="Effort as percentage of FTP (0.5-1.2)"
    )

    @property
    def effective_power_watts(self) -> float:
        """Calculate effective power output for this scenario"""
        return self.rider.ftp_watts * self.effort_percentage