from typing import List
from ..models import EpiData, EconParameters

def calculate_productivity_shock(epi_data: EpiData, params: EconParameters, labour_multipliers: List[float] = None) -> List[float]:
    """
    Calculates the Total Factor Productivity (TFP) multiplier for each time step.
    A multiplier of 1.0 means full baseline productivity.
    
    Logic:
    Productivity drops because:
    1. People are working remotely (which may be less efficient: remote_work_efficiency)
    2. People are working while sick (sick_productivity_factor)
    3. General disruption (supply chain, fear) - we could add a base disruption factor proportional to total cases.
    
    Multiplier_t = Weighted average of productivity of the working population.
    
    Working population at t: W_t = 1.0 - (H_t + D_t + I_t * sick_away_fraction + Q_t * cannot_remote_fraction)
    
    Working but remote (quarantined): Q_t * remote_capacity
    Working but sick: I_t * (1 - sick_away_fraction)
    Working normal: W_t - (Working remote) - (Working sick)
    
    If W_t is 0, productivity multiplier is 0 (though it doesn't matter if labor is 0).
    """
    multipliers = []
    
    sick_away_fraction = 0.9 
    remote_capacity = params.remote_work_capacity
    remote_efficiency = params.remote_work_efficiency
    sick_efficiency = params.sick_productivity_factor
    
    for i in range(len(epi_data.time)):
        h = epi_data.hospitalized[i] if epi_data.hospitalized else 0.0
        d = epi_data.deceased[i] if epi_data.deceased else 0.0
        q = epi_data.quarantined[i] if epi_data.quarantined else 0.0
        infected = epi_data.infectious[i]
        
        # Calculate subpopulations
        working_remote = q * remote_capacity
        working_sick = infected * (1.0 - sick_away_fraction)
        
        reduction = h + d + (infected * sick_away_fraction) + (q * (1.0 - remote_capacity))
        w_t = max(0.0, 1.0 - reduction)
        
        if w_t <= 0.0:
            multipliers.append(0.0)
            continue
            
        working_normal = max(0.0, w_t - working_remote - working_sick)
        
        # Calculate weighted productivity
        total_prod = (
            (working_normal * 1.0) + 
            (working_remote * remote_efficiency) + 
            (working_sick * sick_efficiency)
        )
        
        # TFP multiplier is the average productivity per worker
        avg_prod = total_prod / w_t
        
        # Add a macro friction penalty based on infection prevalence (supply chain disruptions)
        # e.g., for every 1% of population infected, lose 0.5% of overall productivity
        macro_friction = infected * 0.5
        avg_prod = max(0.0, avg_prod - macro_friction)
        
        multipliers.append(avg_prod)
        
    return multipliers
