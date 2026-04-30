import json
from typing import Dict, Any
from ..models import MacroShocks

class CGETranslator:
    """
    Translates OEECF MacroShocks into standard parameters for Computable General Equilibrium (CGE) models.
    CGE models typically use Constant Elasticity of Substitution (CES) production functions.
    This translator outputs shocks as percentage changes from baseline (delta values).
    """
    
    def translate(self, shocks: MacroShocks) -> Dict[str, Any]:
        """
        Converts the time-series multipliers into percentage changes (deltas).
        For example, a multiplier of 0.95 becomes a delta of -0.05.
        """
        cge_params = {
            "time": shocks.time,
            "delta_L": [round(m - 1.0, 4) for m in shocks.labor_supply_multiplier],
        }
        
        if shocks.demand_multiplier:
            cge_params["delta_D"] = [round(m - 1.0, 4) for m in shocks.demand_multiplier]
        
        # Sectoral TFP changes
        delta_A = {}
        for sector_name, multipliers in shocks.productivity_multiplier.items():
            delta_A[f"delta_A_{sector_name}"] = [round(m - 1.0, 4) for m in multipliers]
            
        cge_params.update(delta_A)
        
        return cge_params
        
    def export_json(self, shocks: MacroShocks, filepath: str):
        """
        Exports the translated parameters to a JSON file.
        """
        params = self.translate(shocks)
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=4)
