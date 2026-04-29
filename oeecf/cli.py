import argparse
import sys
import os
import json
import numpy as np

from .models import EpiData, EconParameters, SectorProfile
from .engine import EpiEconCoupler
from .translators.ogcore import OGCoreTranslator

def generate_synthetic_epi_data(days=100):
    """Generates synthetic SIR data for the CLI demo."""
    t = np.arange(days)
    peak_day = days * 0.4
    spread = days * 0.15
    
    infectious = 0.3 * np.exp(-0.5 * ((t - peak_day) / spread) ** 2)
    hospitalized = infectious * 0.1
    quarantined = infectious * 1.5
    deceased = np.cumsum(hospitalized * 0.02)
    
    return EpiData(
        time=t.tolist(),
        susceptible=[1.0]*days,
        infectious=infectious.tolist(),
        recovered=[0.0]*days,
        hospitalized=hospitalized.tolist(),
        deceased=deceased.tolist(),
        quarantined=quarantined.tolist()
    )

def run_simulation(args):
    print(f"Running simulation for {args.days} days...")
    epi_data = generate_synthetic_epi_data(days=args.days)
    
    # Setup Sector Profiles
    sectors = {
        "manufacturing": SectorProfile(remote_work_capacity=0.10, remote_work_efficiency=0.50),
        "services": SectorProfile(remote_work_capacity=0.85, remote_work_efficiency=0.90)
    }
    
    params = EconParameters(
        baseline_participation_rate=0.65,
        sectors=sectors
    )
    
    coupler = EpiEconCoupler(params=params)
    shocks = coupler.generate_shocks(epi_data)
    
    translator = OGCoreTranslator(start_year=args.start_year)
    translator.export_json(shocks, args.output)
    print(f"Exported macroeconomic shocks to {args.output}")

def main():
    parser = argparse.ArgumentParser(description="OEECF Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    run_parser = subparsers.add_parser("run-simulation", help="Run a synthetic coupling simulation")
    run_parser.add_argument("--days", type=int, default=100, help="Number of days to simulate")
    run_parser.add_argument("--start-year", type=int, default=2024, help="Starting year for OG-Core")
    run_parser.add_argument("--output", type=str, default="ogcore_shocks.json", help="Output JSON file path")
    
    args = parser.parse_args()
    
    if args.command == "run-simulation":
        run_simulation(args)

if __name__ == "__main__":
    main()
