import json
from typing import Dict, Any
from ..models import MacroShocks

class OGCoreTranslator:
    """
    Translates OEECF MacroShocks into a format suitable for OG-Core parameters.
    OG-Core typically accepts parameter updates via a JSON dictionary.
    """
    
    def __init__(self, start_year: int = 2020):
        self.start_year = start_year

    def translate(self, shocks: MacroShocks) -> Dict[str, Any]:
        """
        Converts the time-series shocks into OG-Core parameter structures.
        Assuming each time step in the shocks is a year for OG-Core, or we aggregate
        daily/monthly data to annual.
        
        For simplicity, this example assumes `shocks.time` are annual indices 
        (0 = start_year, 1 = start_year+1).
        
        We will output parameters that OG-Core commonly uses, such as:
        - `Z` (Total Factor Productivity multiplier)
        - `L_multiplier` (or modifying the labor endowment/disutility)
        """
        
        # OG-Core typically expects a dictionary where keys are parameter names,
        # and values are lists (time series) or single values.
        
        # In a real implementation, we would aggregate high-frequency SIR data 
        # (e.g., daily) into annual averages because OG-Core is an annual model.
        # Here we just pass the multipliers directly assuming they are already annual,
        # or we just pass them as a generic time series.
        
        ogcore_params = {
            "labor_endowment_multiplier": shocks.labor_supply_multiplier,
            "start_year": self.start_year
        }
        
        # If there's only a 'global' sector, map it to the standard 'Z' parameter.
        # Otherwise, prefix with 'Z_' for each sector.
        if "global" in shocks.productivity_multiplier and len(shocks.productivity_multiplier) == 1:
            ogcore_params["Z"] = shocks.productivity_multiplier["global"]
        else:
            for sector_name, multipliers in shocks.productivity_multiplier.items():
                ogcore_params[f"Z_{sector_name}"] = multipliers
        
        return ogcore_params
        
    def export_json(self, shocks: MacroShocks, filepath: str):
        """
        Exports the translated parameters to a JSON file.
        """
        params = self.translate(shocks)
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=4)
