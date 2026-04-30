import pytest
from oeecf.models import EpiData, EconParameters
from oeecf.engine import EpiEconCoupler

def test_engine_generate_shocks_basic():
    # Setup baseline parameters
    params = EconParameters(
        baseline_participation_rate=0.6,
        remote_work_capacity=0.5,
        remote_work_efficiency=1.0,
        sick_productivity_factor=0.0
    )
    
    # Create a simple epidemic scenario
    epi_data = EpiData(
        time=[1, 2, 3],
        susceptible=[1.0, 0.9, 0.8],
        infectious=[0.0, 0.1, 0.2],
        recovered=[0.0, 0.0, 0.0]
    )
    
    coupler = EpiEconCoupler(params)
    shocks = coupler.generate_shocks(epi_data)
    
    # Assertions on lengths
    assert len(shocks.time) == 3
    assert len(shocks.labor_supply_multiplier) == 3
    assert "global" in shocks.productivity_multiplier
    assert len(shocks.productivity_multiplier["global"]) == 3
    
    # At time 1, 0 infectious -> multipliers should be 1.0
    assert shocks.labor_supply_multiplier[0] == 1.0
    assert shocks.productivity_multiplier["global"][0] == 1.0

def test_engine_with_hospitalization_overflow():
    params = EconParameters(
        hospital_capacity=0.05,
        base_fatality_rate=0.02,
        overflow_fatality_multiplier=3.0
    )
    
    epi_data = EpiData(
        time=[1, 2],
        susceptible=[0.9, 0.8],
        infectious=[0.1, 0.1],
        recovered=[0.0, 0.0],
        hospitalized=[0.02, 0.10], # Exceeds capacity at t=2
        deceased=[0.0, 0.0]
    )
    
    coupler = EpiEconCoupler(params)
    shocks = coupler.generate_shocks(epi_data)
    
    # Labor supply should drop more at t=2 due to hospitalization and excess death
    assert shocks.labor_supply_multiplier[1] < shocks.labor_supply_multiplier[0]
