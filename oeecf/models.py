from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class EpiData(BaseModel):
    """
    Time-series output from an epidemiological model (e.g., SIR, SEIR).
    Each list represents a timeseries of population fractions (0.0 to 1.0) 
    or absolute numbers at each time step (e.g., days).
    """
    time: List[int] = Field(..., description="Time steps (e.g., days)")
    susceptible: List[float] = Field(..., description="Susceptible population fraction/count")
    exposed: Optional[List[float]] = Field(None, description="Exposed population fraction/count")
    infectious: List[float] = Field(..., description="Infectious population fraction/count")
    recovered: List[float] = Field(..., description="Recovered population fraction/count")
    hospitalized: Optional[List[float]] = Field(None, description="Hospitalized population fraction/count")
    deceased: Optional[List[float]] = Field(None, description="Deceased population fraction/count")
    quarantined: Optional[List[float]] = Field(None, description="Quarantined (but not necessarily infectious) population fraction/count")

    # To ensure all lists are of the same length
    def validate_lengths(self):
        length = len(self.time)
        for attr in ['susceptible', 'exposed', 'infectious', 'recovered', 'hospitalized', 'deceased', 'quarantined']:
            val = getattr(self, attr)
            if val is not None and len(val) != length:
                raise ValueError(f"Length of {attr} ({len(val)}) does not match length of time ({length})")

class SectorProfile(BaseModel):
    """
    Economic parameters specific to a single sector.
    """
    remote_work_capacity: float = Field(..., description="Fraction of jobs that can be done remotely in this sector")
    remote_work_efficiency: float = Field(0.80, description="Relative efficiency of remote work compared to in-person")


class EconParameters(BaseModel):
    """
    Baseline economic parameters used to calculate shocks.
    """
    baseline_participation_rate: float = Field(0.65, description="Baseline fraction of total population in the labor force")
    remote_work_capacity: float = Field(0.35, description="Global fraction of jobs that can be done remotely")
    remote_work_efficiency: float = Field(0.80, description="Global relative efficiency of remote work compared to in-person (1.0 = equal)")
    sick_productivity_factor: float = Field(0.10, description="Productivity factor for infectious people who are still working (often close to 0)")
    quarantine_productivity_factor: float = Field(0.50, description="Productivity of quarantined healthy individuals (depends on remote work)")
    hospitalization_productivity_factor: float = Field(0.0, description="Productivity of hospitalized individuals (always 0)")
    sectors: Dict[str, SectorProfile] = Field(default_factory=dict, description="Optional sector-specific profiles")

class MacroShocks(BaseModel):
    """
    The calculated economic shocks over time, to be fed into a macro model.
    Multipliers are typically 1.0 in a steady state (no epidemic) and drop below 1.0 during an epidemic.
    """
    time: List[int]
    labor_supply_multiplier: List[float] = Field(..., description="Multiplier for baseline labor supply (L)")
    productivity_multiplier: Dict[str, List[float]] = Field(..., description="Multiplier for Total Factor Productivity by sector (or 'global')")
