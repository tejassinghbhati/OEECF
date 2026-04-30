import argparse
import sys
import os
import json
import numpy as np
import logging

from .models import EpiData, EconParameters, SectorProfile
from .engine import EpiEconCoupler
from .translators.ogcore import OGCoreTranslator

def setup_logger(verbose=False):
    """Configures the root logger based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def generate_synthetic_epi_data(days=100):
    """Generates synthetic SIR data for the CLI demo."""
    logging.debug(f"Generating synthetic epi data for {days} days")
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
    logging.info(f"Running simulation for {args.days} days...")
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
    
    logging.debug("Initializing EpiEconCoupler")
    coupler = EpiEconCoupler(params=params)
    shocks = coupler.generate_shocks(epi_data)
    
    logging.debug(f"Exporting to OG-Core JSON format (start_year={args.start_year})")
    translator = OGCoreTranslator(start_year=args.start_year)
    translator.export_json(shocks, args.output)
    logging.info(f"Exported macroeconomic shocks to {args.output}")

def main():
    parser = argparse.ArgumentParser(description="OEECF Command Line Interface")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    run_parser = subparsers.add_parser("run-simulation", help="Run a synthetic coupling simulation")
    run_parser.add_argument("--days", type=int, default=100, help="Number of days to simulate")
    run_parser.add_argument("--start-year", type=int, default=2024, help="Starting year for OG-Core")
    run_parser.add_argument("--output", type=str, default="ogcore_shocks.json", help="Output JSON file path")
    
    args = parser.parse_args()
    setup_logger(args.verbose)
    
    if args.command == "run-simulation":
        run_simulation(args)

if __name__ == "__main__":
    main()
