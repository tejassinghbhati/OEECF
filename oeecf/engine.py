from .models import EpiData, EconParameters, MacroShocks
from .shocks.labour import calculate_labour_supply_shock
from .shocks.productivity import calculate_productivity_shock

class EpiEconCoupler:
    """
    The main orchestrator that takes epidemiological data and economic parameters,
    and produces macroeconomic shocks.
    """
    
    def __init__(self, params: EconParameters = None):
        if params is None:
            self.params = EconParameters()
        else:
            self.params = params
            
    def generate_shocks(self, epi_data: EpiData) -> MacroShocks:
        """
        Runs the shock calculators and returns the MacroShocks.
        """
        # Validate data
        epi_data.validate_lengths()
        
        # Calculate Labor Supply Shock
        labor_multipliers = calculate_labour_supply_shock(epi_data, self.params)
        
        # Calculate Productivity Shock
        prod_multipliers = calculate_productivity_shock(epi_data, self.params, labor_multipliers)
        
        shocks = MacroShocks(
            time=epi_data.time,
            labor_supply_multiplier=labor_multipliers,
            productivity_multiplier=prod_multipliers
        )
        
        return shocks
