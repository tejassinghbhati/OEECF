from typing import List
from ..models import EpiData, EconParameters
from .. import constants

def calculate_demand_shock(epi_data: EpiData, params: EconParameters) -> List[float]:
    """
    Calculates the consumption demand multiplier for each time step.
    A multiplier of 1.0 means baseline consumption.
    
    The logic:
    Demand drops due to two main factors during an epidemic:
    1. Fear of infection (people stay home, don't spend on services)
    2. Quarantine mandates
    
    Demand Multiplier = 1.0 - (Infectious * fear_factor) - (Quarantined * quarantine_demand_drop)
    """
    multipliers = []
    
    # How much demand drops per infected percentage point (social distancing)
    fear_factor = getattr(params, 'fear_factor_multiplier', constants.DEFAULT_FEAR_FACTOR)
    
    # How much demand drops for someone in quarantine
    quarantine_drop = constants.QUARANTINE_DEMAND_DROP
    
    for i in range(len(epi_data.time)):
        infected = epi_data.infectious[i]
        q = epi_data.quarantined[i] if epi_data.quarantined else 0.0
        
        reduction = (infected * fear_factor) + (q * quarantine_drop)
        
        # Demand shouldn't drop below a minimum subsistence level (e.g. 0.2)
        multiplier = max(constants.MINIMUM_SUBSISTENCE_DEMAND, 1.0 - reduction)
        multipliers.append(multiplier)
        
    return multipliers
