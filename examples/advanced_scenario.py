import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from oeecf.models import EpiData, EconParameters, SectorProfile
from oeecf.engine import EpiEconCoupler
from oeecf.translators.cge import CGETranslator

def generate_epi_curve(days=150, mitigation=False):
    t = np.arange(days)
    peak_day = 60
    spread = 20 if mitigation else 12
    peak_val = 0.15 if mitigation else 0.40
    
    infectious = peak_val * np.exp(-0.5 * ((t - peak_day) / spread) ** 2)
    hospitalized = infectious * 0.15 
    quarantined = infectious * 1.5
    deceased = np.cumsum(hospitalized * 0.01)
    
    return EpiData(
        time=t.tolist(),
        susceptible=[1.0]*days,
        infectious=infectious.tolist(),
        recovered=[0.0]*days,
        hospitalized=hospitalized.tolist(),
        deceased=deceased.tolist(),
        quarantined=quarantined.tolist()
    )

def main():
    days = 150
    # Create two scenarios
    epi_mitigated = generate_epi_curve(days, mitigation=True)
    epi_unmitigated = generate_epi_curve(days, mitigation=False)
    
    sectors = {
        "manufacturing": SectorProfile(remote_work_capacity=0.10, remote_work_efficiency=0.50),
        "services": SectorProfile(remote_work_capacity=0.85, remote_work_efficiency=0.90)
    }
    
    # 5% hospital capacity threshold
    params = EconParameters(
        hospital_capacity=0.03, # 3% capacity for this example
        base_fatality_rate=0.02,
        overflow_fatality_multiplier=5.0, # 5x death rate if hospitals overflow
        sectors=sectors
    )
    
    coupler = EpiEconCoupler(params=params)
    
    shocks_mitigated = coupler.generate_shocks(epi_mitigated)
    shocks_unmitigated = coupler.generate_shocks(epi_unmitigated)
    
    translator = CGETranslator()
    translator.export_json(shocks_mitigated, "cge_shocks_mitigated.json")
    translator.export_json(shocks_unmitigated, "cge_shocks_unmitigated.json")
    print("Exported CGE parameters.")
    
    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
    
    # Scenario 1: Mitigated
    axes[0].plot(epi_mitigated.time, epi_mitigated.hospitalized, label='Hospitalized', color='red')
    axes[0].axhline(y=params.hospital_capacity, color='black', linestyle=':', label='Hospital Capacity')
    axes[0].plot(shocks_mitigated.time, shocks_mitigated.labor_supply_multiplier, label='Labor Supply Multiplier', color='blue')
    axes[0].set_title('Scenario A: Flattened Curve (Under Capacity)')
    axes[0].set_xlabel('Time (Days)')
    axes[0].set_ylabel('Fraction / Multiplier')
    axes[0].legend()
    axes[0].grid(True)
    
    # Scenario 2: Unmitigated
    axes[1].plot(epi_unmitigated.time, epi_unmitigated.hospitalized, label='Hospitalized', color='red')
    axes[1].axhline(y=params.hospital_capacity, color='black', linestyle=':', label='Hospital Capacity')
    axes[1].plot(shocks_unmitigated.time, shocks_unmitigated.labor_supply_multiplier, label='Labor Supply Multiplier', color='blue')
    axes[1].set_title('Scenario B: Unmitigated (Capacity Collapse)')
    axes[1].set_xlabel('Time (Days)')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig("capacity_shock_curves.png")
    print("Saved plot to capacity_shock_curves.png")

if __name__ == "__main__":
    main()
