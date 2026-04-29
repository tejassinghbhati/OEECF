from typing import List, Dict
from ..models import EpiData, EconParameters

def calculate_productivity_shock(epi_data: EpiData, params: EconParameters, labour_multipliers: List[float] = None) -> Dict[str, List[float]]:
    """
    Calculates the Total Factor Productivity (TFP) multiplier for each time step by sector.
    """
    sick_away_fraction = 0.9 
    sick_efficiency = params.sick_productivity_factor
    
    # Determine the sectors to calculate. If none, use a single 'global' sector
    sectors_to_run = {}
    if not params.sectors:
        sectors_to_run["global"] = {
            "remote_capacity": params.remote_work_capacity,
            "remote_efficiency": params.remote_work_efficiency
        }
    else:
        for name, profile in params.sectors.items():
            sectors_to_run[name] = {
                "remote_capacity": profile.remote_work_capacity,
                "remote_efficiency": profile.remote_work_efficiency
            }

    results = {}
    
    for sector_name, props in sectors_to_run.items():
        multipliers = []
        remote_capacity = props["remote_capacity"]
        remote_efficiency = props["remote_efficiency"]
        
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
            macro_friction = infected * 0.5
            avg_prod = max(0.0, avg_prod - macro_friction)
            
            multipliers.append(avg_prod)
            
        results[sector_name] = multipliers
        
    return results
