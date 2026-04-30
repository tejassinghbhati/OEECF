import matplotlib.pyplot as plt
from typing import Optional
from ..models import EpiData, MacroShocks

def plot_shocks(epi_data: EpiData, shocks: MacroShocks, save_path: Optional[str] = None):
    """
    Plots the epidemiological data and the resulting macroeconomic shocks side-by-side.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot Epidemiological Data
    ax1.plot(epi_data.time, epi_data.susceptible, label='Susceptible', color='blue')
    ax1.plot(epi_data.time, epi_data.infectious, label='Infectious', color='red')
    ax1.plot(epi_data.time, epi_data.recovered, label='Recovered', color='green')
    if epi_data.hospitalized:
        ax1.plot(epi_data.time, epi_data.hospitalized, label='Hospitalized', color='purple', linestyle='--')
    
    ax1.set_title('Epidemiological Dynamics')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Population Fraction')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot Macroeconomic Shocks
    ax2.plot(shocks.time, shocks.labor_supply_multiplier, label='Labor Supply Multiplier', color='black', linewidth=2)
    
    for sector, multipliers in shocks.productivity_multiplier.items():
        ax2.plot(shocks.time, multipliers, label=f'TFP Multiplier ({sector})', linestyle='--')
        
    if shocks.demand_multiplier:
        ax2.plot(shocks.time, shocks.demand_multiplier, label='Demand Multiplier', color='orange', linestyle=':')
        
    ax2.set_title('Macroeconomic Shocks')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Multiplier (1.0 = Baseline)')
    ax2.set_ylim(0.0, 1.1)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
