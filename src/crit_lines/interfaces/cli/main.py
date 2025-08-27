#!/usr/bin/env python3
"""
Crit Lines CLI - Cycling Performance Simulation Tool
"""

import sys
from pathlib import Path
from typing import List, Optional

import click

from ...core.analysis_engine.simulator import CourseSimulator
from ...core.data_models.bike import Bike, BikeConfig, BikeType, WheelType
from ...core.data_models.course import CourseConditions, WindConditions
from ...core.data_models.gpx_parser import GPXParser
from ...core.data_models.rider import Rider, RiderConfig, RidingPosition
from ...visualization.plotter import CritLinesPlotter


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Crit Lines - Cycling Performance Simulation Tool
    
    Analyze cycling performance on courses using physics-based simulation.
    Compare different rider weights, FTP levels, and equipment configurations.
    """
    pass


@cli.command()
@click.argument('gpx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--weight', '-w', type=float, default=70.0, help='Rider weight in kg')
@click.option('--ftp', '-f', type=float, default=250.0, help='FTP in watts')
@click.option('--effort', '-e', type=float, default=1.0, help='Effort as fraction of FTP (0.5-1.2)')
@click.option('--bike-weight', type=float, default=8.0, help='Bike weight in kg')
@click.option('--position', type=click.Choice(['drops', 'hoods', 'tops', 'aero_bars']), 
              default='hoods', help='Riding position')
@click.option('--wheels', type=click.Choice(['standard', 'aero_shallow', 'aero_deep', 'disc', 'climbing']),
              default='standard', help='Wheel type')
@click.option('--temp', type=float, default=20.0, help='Temperature in Celsius')
@click.option('--wind-speed', type=float, default=0.0, help='Wind speed in km/h')
@click.option('--wind-direction', type=float, default=0.0, help='Wind direction in degrees (0-360)')
@click.option('--plot/--no-plot', default=True, help='Generate elevation and power plots')
def simulate(gpx_file: Path, weight: float, ftp: float, effort: float, 
             bike_weight: float, position: str, wheels: str, temp: float,
             wind_speed: float, wind_direction: float, plot: bool):
    """Simulate performance on a GPX course"""
    
    try:
        # Parse GPX file
        click.echo(f"Loading course from {gpx_file.name}...")
        parser = GPXParser()
        course = parser.parse_gpx_file(gpx_file)
        
        # Create rider configuration
        rider = Rider(
            weight_kg=weight,
            ftp_watts=ftp,
            position=RidingPosition(position)
        )
        rider_config = RiderConfig(
            name="Rider",
            rider=rider,
            effort_percentage=effort
        )
        
        # Create bike configuration
        bike = Bike(
            bike_type=BikeType.ROAD,
            weight_kg=bike_weight,
            wheel_type=WheelType(wheels)
        )
        bike_config = BikeConfig(name="Bike", bike=bike)
        
        # Set up conditions
        wind = WindConditions(speed_kmh=wind_speed, direction_degrees=wind_direction) if wind_speed > 0 else None
        conditions = CourseConditions(
            temperature_c=temp,
            humidity_percent=50.0,
            wind=wind
        )
        
        # Run simulation
        simulator = CourseSimulator()
        result = simulator.simulate_course(course, rider_config, bike_config, conditions)
        
        # Display results
        _display_results(course, result)
        
        # Generate plots if requested
        if plot:
            plotter = CritLinesPlotter()
            plotter.plot_elevation_profile(course, result, f"{gpx_file.stem}_elevation.png")
            plotter.plot_power_analysis(course, result, f"{gpx_file.stem}_power.png")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('gpx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--base-weight', type=float, default=70.0, help='Base rider weight in kg')
@click.option('--weight-range', type=str, default='65,70,75', 
              help='Comma-separated weight values to compare')
@click.option('--ftp', type=float, default=250.0, help='FTP in watts')
@click.option('--effort', type=float, default=1.0, help='Effort as fraction of FTP')
@click.option('--temp', type=float, default=20.0, help='Temperature in Celsius')
@click.option('--plot/--no-plot', default=True, help='Generate comparison chart')
def compare_weight(gpx_file: Path, base_weight: float, weight_range: str,
                  ftp: float, effort: float, temp: float, plot: bool):
    """Compare performance at different rider weights"""
    
    try:
        # Parse weights
        weights = [float(w.strip()) for w in weight_range.split(',')]
        
        # Load course
        parser = GPXParser()
        course = parser.parse_gpx_file(gpx_file)
        
        # Base configuration
        base_rider = Rider(weight_kg=base_weight, ftp_watts=ftp)
        base_config = RiderConfig(name="Base", rider=base_rider, effort_percentage=effort)
        bike_config = BikeConfig(name="Standard", bike=Bike(weight_kg=8.0))
        conditions = CourseConditions(temperature_c=temp, humidity_percent=50.0)
        
        # Run analysis
        simulator = CourseSimulator()
        results = simulator.analyze_weight_impact(course, base_config, bike_config, conditions, weights)
        
        # Display comparison
        _display_comparison(results, "Weight Comparison")
        
        # Generate plot if requested
        if plot:
            plotter = CritLinesPlotter()
            plotter.plot_comparison_chart(results, "Weight Comparison", f"{gpx_file.stem}_weight_comparison.png")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('gpx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--weight', type=float, default=70.0, help='Rider weight in kg')
@click.option('--base-ftp', type=float, default=250.0, help='Base FTP in watts')
@click.option('--ftp-range', type=str, default='230,250,270', 
              help='Comma-separated FTP values to compare')
@click.option('--effort', type=float, default=1.0, help='Effort as fraction of FTP')
@click.option('--temp', type=float, default=20.0, help='Temperature in Celsius')
@click.option('--plot/--no-plot', default=True, help='Generate comparison chart')
def compare_power(gpx_file: Path, weight: float, base_ftp: float, ftp_range: str,
                 effort: float, temp: float, plot: bool):
    """Compare performance at different FTP levels"""
    
    try:
        # Parse FTP values
        ftps = [float(f.strip()) for f in ftp_range.split(',')]
        
        # Load course
        parser = GPXParser()
        course = parser.parse_gpx_file(gpx_file)
        
        # Base configuration
        base_rider = Rider(weight_kg=weight, ftp_watts=base_ftp)
        base_config = RiderConfig(name="Base", rider=base_rider, effort_percentage=effort)
        bike_config = BikeConfig(name="Standard", bike=Bike(weight_kg=8.0))
        conditions = CourseConditions(temperature_c=temp, humidity_percent=50.0)
        
        # Run analysis
        simulator = CourseSimulator()
        results = simulator.analyze_power_impact(course, base_config, bike_config, conditions, ftps)
        
        # Display comparison
        _display_comparison(results, "Power Comparison")
        
        # Generate plot if requested  
        if plot:
            plotter = CritLinesPlotter()
            plotter.plot_comparison_chart(results, "Power Comparison", f"{gpx_file.stem}_power_comparison.png")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def sample():
    """Run simulation on sample course (for testing)"""
    
    try:
        # Create sample course
        parser = GPXParser()
        course = parser.create_sample_course()
        
        # Default configuration
        rider = Rider(weight_kg=70.0, ftp_watts=250.0)
        rider_config = RiderConfig(name="Sample Rider", rider=rider)
        bike_config = BikeConfig(name="Sample Bike", bike=Bike(weight_kg=8.0))
        conditions = CourseConditions(temperature_c=20.0, humidity_percent=50.0)
        
        # Run simulation
        simulator = CourseSimulator()
        result = simulator.simulate_course(course, rider_config, bike_config, conditions)
        
        # Display results
        _display_results(course, result)
        
        # Generate sample plots
        plotter = CritLinesPlotter()
        plotter.plot_elevation_profile(course, result, "sample_elevation.png")
        plotter.plot_power_analysis(course, result, "sample_power.png")
        
        click.echo("\n🎯 Next steps:")
        click.echo("• View the generated plots: sample_elevation.png, sample_power.png")
        click.echo("• Download a GPX file from Strava and run:")
        click.echo("  ./venv/bin/python run.py simulate your-ride.gpx --weight 70 --ftp 250")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _display_results(course, result):
    """Display simulation results"""
    click.echo("\n" + "="*60)
    click.echo(f"COURSE: {course.name}")
    click.echo("="*60)
    
    click.echo(f"Distance: {course.total_distance_km:.1f} km")
    click.echo(f"Elevation gain: {course.total_elevation_gain_m:.0f} m")
    click.echo(f"Max gradient: {course.max_gradient_percent:.1f}%")
    click.echo(f"Min gradient: {course.min_gradient_percent:.1f}%")
    
    click.echo("\n" + "-"*40)
    click.echo("SIMULATION RESULTS")
    click.echo("-"*40)
    
    click.echo(f"Total time: {result.total_time_formatted}")
    click.echo(f"Average speed: {result.average_speed_kmh:.1f} km/h")
    click.echo(f"Average power: {result.average_power_watts:.0f} W")
    
    # Power metrics
    power_to_weight = result.rider_config.rider.power_to_weight_ratio
    click.echo(f"Power-to-weight ratio: {power_to_weight:.2f} W/kg")
    
    # Course difficulty
    click.echo(f"Course difficulty score: {course.course_difficulty_score:.1f}")


def _display_comparison(results: List, title: str):
    """Display comparison results"""
    click.echo("\n" + "="*60)
    click.echo(title.upper())
    click.echo("="*60)
    
    if not results:
        click.echo("No results to display")
        return
    
    # Table header
    click.echo(f"{'Scenario':<20} {'Time':<10} {'Speed':<8} {'Δ Time':<8}")
    click.echo("-" * 50)
    
    # Reference time (first/fastest result)
    reference_time = results[0].total_time_seconds
    
    for result in results:
        time_diff = result.total_time_seconds - reference_time
        time_diff_str = f"+{time_diff:.0f}s" if time_diff > 0 else f"{time_diff:.0f}s"
        
        click.echo(
            f"{result.scenario_name:<20} "
            f"{result.total_time_formatted:<10} "
            f"{result.average_speed_kmh:.1f}km/h  "
            f"{time_diff_str:<8}"
        )


def main():
    """Entry point for the CLI application"""
    cli()