import sys
import os

# Add the parent directory to the path so we can import oeecf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from oeecf.models import EpiData, EconParameters
from oeecf.engine import EpiEconCoupler
from oeecf.translators.ogcore import OGCoreTranslator

def generate_synthetic_epi_data(days=100):
    """
    Generates a synthetic, simplified SIR-like curve for demonstration.
    """
    t = np.arange(days)
    
    # Peak infection around day 40
    peak_day = 40
    spread = 15
    
    infectious = 0.3 * np.exp(-0.5 * ((t - peak_day) / spread) ** 2)
    hospitalized = infectious * 0.1 # 10% of infectious are hospitalized
    quarantined = infectious * 1.5  # 1.5x infectious are quarantined (contacts)
    deceased = np.cumsum(hospitalized * 0.02) # 2% of hospitalized die
    
    susceptible = 1.0 - (infectious + recovered(infectious) + deceased) # Simplified
    # For this example, we just pass the required arrays
    
    return EpiData(
        time=t.tolist(),
        susceptible=[1.0]*days, # Dummy
        infectious=infectious.tolist(),
        recovered=[0.0]*days, # Dummy
        hospitalized=hospitalized.tolist(),
        deceased=deceased.tolist(),
        quarantined=quarantined.tolist()
    )

def recovered(infectious):
    return np.cumsum(infectious) * 0.05 # Dummy cumulative sum for demo

def main():
    print("Generating synthetic epidemiological data...")
    epi_data = generate_synthetic_epi_data(days=100)
    
    print("Initializing OEECF Coupler...")
    from oeecf.models import SectorProfile
    
    sectors = {
        "manufacturing": SectorProfile(remote_work_capacity=0.10, remote_work_efficiency=0.50),
        "services": SectorProfile(remote_work_capacity=0.85, remote_work_efficiency=0.90)
    }
    
    params = EconParameters(
        baseline_participation_rate=0.65,
        sectors=sectors
    )
    
    coupler = EpiEconCoupler(params=params)
    
    print("Generating macroeconomic shocks...")
    shocks = coupler.generate_shocks(epi_data)
    
    print("Translating to OG-Core format...")
    translator = OGCoreTranslator(start_year=2020)
    ogcore_params = translator.translate(shocks)
    
    # Save the output
    output_path = "ogcore_shocks.json"
    translator.export_json(shocks, output_path)
    print(f"Exported OG-Core parameters to {output_path}")
    
    # Plotting the results
    plt.figure(figsize=(10, 6))
    
    plt.plot(epi_data.time, epi_data.infectious, label='Infectious Fraction', color='red', linestyle='--')
    plt.plot(shocks.time, shocks.labor_supply_multiplier, label='Labor Supply Multiplier', color='blue')
    
    colors = ['green', 'orange', 'purple']
    for idx, (sector_name, multipliers) in enumerate(shocks.productivity_multiplier.items()):
        plt.plot(shocks.time, multipliers, label=f'Productivity ({sector_name})', color=colors[idx % len(colors)])
    
    plt.title('Epidemiological Shocks to Macroeconomic Variables (Sectoral)')
    plt.xlabel('Time (Days)')
    plt.ylabel('Multiplier / Fraction')
    plt.ylim(0, 1.1)
    plt.legend()
    plt.grid(True)
    
    # Save the plot
    plt.savefig("shock_curves.png")
    print("Saved plot to shock_curves.png")

if __name__ == "__main__":
    main()
