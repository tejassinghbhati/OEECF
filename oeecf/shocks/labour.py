from typing import List
from ..models import EpiData, EconParameters

def calculate_labour_supply_shock(epi_data: EpiData, params: EconParameters) -> List[float]:
    """
    Calculates the labor supply multiplier for each time step.
    A multiplier of 1.0 means full baseline labor supply.
    
    The logic:
    We assume the baseline labor supply is L_base = baseline_participation_rate * Pop
    During an epidemic, the active labor supply is reduced by:
    - Hospitalized people (100% removed from labor force)
    - Deceased people (100% removed)
    - Sick/Infectious people who are too sick to work (assume a fraction of infectious)
    - Quarantined people who cannot work remotely
    
    For simplicity in V1, we assume:
    Labor Multiplier = 1.0 - (Hospitalized + Deceased + (Infectious * (1 - sick_participation_rate)) + Quarantined * (1 - remote_capacity))
    Wait, to keep it simple and strictly bounded, we look at the reduction as a fraction of the total population, 
    then scale by participation rate, but since both are scaled, the multiplier is just the fraction of the workforce still working.
    
    Multiplier_t = 1.0 - (H_t + D_t + I_t * sick_away_fraction + Q_t * cannot_remote_fraction)
    
    If H, D, Q are None, they are treated as 0.
    """
    multipliers = []
    
    # Assume 90% of infectious people are too sick to work (if not hospitalized)
    sick_away_fraction = 0.9 
    # Fraction of quarantined who cannot work remotely
    cannot_remote_fraction = 1.0 - params.remote_work_capacity
    
    cumulative_excess_deaths = 0.0

    for i in range(len(epi_data.time)):
        h = epi_data.hospitalized[i] if epi_data.hospitalized else 0.0
        d = epi_data.deceased[i] if epi_data.deceased else 0.0
        q = epi_data.quarantined[i] if epi_data.quarantined else 0.0
        infected = epi_data.infectious[i]
        
        # Healthcare Capacity Dynamics
        # If hospitalizations exceed capacity, mortality spikes non-linearly.
        if h > params.hospital_capacity:
            overflow = h - params.hospital_capacity
            # Calculate excess deaths for this time step (assuming time steps are small enough e.g., daily)
            excess_deaths_today = overflow * params.base_fatality_rate * params.overflow_fatality_multiplier
            cumulative_excess_deaths += excess_deaths_today
        
        # Total deceased is original deceased + our calculated excess deaths
        adjusted_d = d + cumulative_excess_deaths
        
        # Reduction in workforce fraction
        reduction = h + adjusted_d + (infected * sick_away_fraction) + (q * cannot_remote_fraction)
        
        # Ensure it doesn't go below 0 (can't have negative labor)
        multiplier = max(0.0, 1.0 - reduction)
        multipliers.append(multiplier)
        
    return multipliers
