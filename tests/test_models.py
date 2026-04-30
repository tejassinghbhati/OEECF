import pytest
from oeecf.models import EpiData, EconParameters, SectorProfile

def test_epidata_validation():
    # Valid EpiData
    data = EpiData(
        time=[1, 2, 3],
        susceptible=[0.9, 0.8, 0.7],
        infectious=[0.1, 0.2, 0.3],
        recovered=[0.0, 0.0, 0.0]
    )
    data.validate_lengths() # Should not raise

    # Invalid EpiData (length mismatch)
    with pytest.raises(ValueError, match="does not match length of time"):
        invalid_data = EpiData(
            time=[1, 2, 3],
            susceptible=[0.9, 0.8], # Only 2 elements
            infectious=[0.1, 0.2, 0.3],
            recovered=[0.0, 0.0, 0.0]
        )
        invalid_data.validate_lengths()

def test_econparameters_defaults():
    params = EconParameters()
    assert params.baseline_participation_rate == 0.65
    assert params.remote_work_capacity == 0.35
    assert len(params.sectors) == 0

def test_econparameters_with_sectors():
    sector_profile = SectorProfile(remote_work_capacity=0.5, remote_work_efficiency=0.9)
    params = EconParameters(sectors={"Tech": sector_profile})
    assert len(params.sectors) == 1
    assert params.sectors["Tech"].remote_work_capacity == 0.5
