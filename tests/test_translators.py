import pytest
from oeecf.models import MacroShocks
from oeecf.translators.ogcore import OGCoreTranslator
from oeecf.translators.cge import CGETranslator
import os
import json

def test_export_to_ogcore(tmp_path):
    shocks = MacroShocks(
        time=[1, 2, 3],
        labor_supply_multiplier=[1.0, 0.9, 0.8],
        productivity_multiplier={"global": [1.0, 0.95, 0.90]},
        demand_multiplier=[1.0, 0.8, 0.6]
    )
    
    out_file = tmp_path / "ogcore_shocks.json"
    translator = OGCoreTranslator()
    translator.export_json(shocks, str(out_file))
    
    assert out_file.exists()
    
    with open(out_file, 'r') as f:
        data = json.load(f)
        
    assert "labor_endowment_multiplier" in data
    assert "Z" in data
    assert "demand_multiplier" in data
    assert len(data["labor_endowment_multiplier"]) == 3

def test_export_to_cge(tmp_path):
    shocks = MacroShocks(
        time=[1, 2, 3],
        labor_supply_multiplier=[1.0, 0.9, 0.8],
        productivity_multiplier={
            "Agri": [1.0, 0.95, 0.90],
            "Tech": [1.0, 0.99, 0.98]
        },
        demand_multiplier=[1.0, 0.8, 0.6]
    )
    
    out_file = tmp_path / "cge_shocks.json"
    translator = CGETranslator()
    translator.export_json(shocks, str(out_file))
    
    assert out_file.exists()
    
    with open(out_file, 'r') as f:
        data = json.load(f)
        
    assert "delta_L" in data
    assert "delta_A_Agri" in data
    assert "delta_A_Tech" in data
    assert "delta_D" in data

