import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List
import numpy as np
from pathlib import Path

from ..core.analysis_engine.simulator import SimulationResult
from ..core.data_models.course import Course


class CritLinesPlotter:
    """Create visualizations for cycling simulation results"""
    
    def __init__(self, save_plots: bool = True, show_plots: bool = False):
        """
        Initialize plotter
        
        Args:
            save_plots: Save plots to files
            show_plots: Display plots (requires GUI)
        """
        self.save_plots = save_plots
        self.show_plots = show_plots
        
        # Set style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def plot_elevation_profile(self, course: Course, result: SimulationResult, filename: str = "elevation_profile.png"):
        """Plot course elevation profile with speed overlay"""
        
        # Extract data
        distances = []
        elevations = []
        speeds = []
        gradients = []
        
        cumulative_distance = 0
        
        for i, segment in enumerate(course.segments):
            distances.append(cumulative_distance)
            elevations.append(segment.start_point.elevation_m)
            if i < len(result.segment_results):
                speeds.append(result.segment_results[i].average_speed_kmh)
            gradients.append(segment.gradient_percent)
            cumulative_distance += segment.distance_m / 1000  # Convert to km
        
        # Add final point
        if course.segments:
            distances.append(cumulative_distance)
            elevations.append(course.segments[-1].end_point.elevation_m)
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        
        # Elevation profile
        ax1.fill_between(distances, elevations, alpha=0.3, color='brown')
        ax1.plot(distances, elevations, color='brown', linewidth=2)
        ax1.set_ylabel('Elevation (m)', fontsize=12)
        ax1.set_title(f'Course Analysis: {course.name}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Speed profile
        if speeds:
            speed_colors = ['red' if s < 15 else 'orange' if s < 25 else 'green' for s in speeds]
            segment_distances = distances[:-1] if len(distances) > len(speeds) else distances[:len(speeds)]
            widths = np.diff(distances) if len(distances) > 1 else [0.1] * len(speeds)
            if len(widths) > len(speeds):
                widths = widths[:len(speeds)]
            ax2.bar(segment_distances, speeds, width=widths, 
                    color=speed_colors, alpha=0.7, align='edge')
            ax2.set_ylabel('Speed (km/h)', fontsize=12)
            ax2.set_ylim(0, max(speeds) * 1.1)
        ax2.grid(True, alpha=0.3)
        
        # Gradient profile  
        gradient_colors = ['red' if g > 5 else 'orange' if g > 2 else 'blue' if g < -2 else 'green' 
                          for g in gradients]
        segment_distances = distances[:-1] if len(distances) > len(gradients) else distances[:len(gradients)]
        widths = np.diff(distances) if len(distances) > 1 else [0.1] * len(gradients)
        if len(widths) > len(gradients):
            widths = widths[:len(gradients)]
        ax3.bar(segment_distances, gradients, width=widths, 
                color=gradient_colors, alpha=0.7, align='edge')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.set_ylabel('Gradient (%)', fontsize=12)
        ax3.set_xlabel('Distance (km)', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # Add summary text
        summary_text = (
            f"Total Time: {result.total_time_formatted}\n"
            f"Avg Speed: {result.average_speed_kmh:.1f} km/h\n"
            f"Avg Power: {result.average_power_watts:.0f} W\n"
            f"Elevation Gain: {course.total_elevation_gain_m:.0f} m"
        )
        
        ax1.text(0.02, 0.98, summary_text, transform=ax1.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Elevation profile saved: {filename}")
        
        if self.show_plots:
            plt.show()
        else:
            plt.close()
    
    def plot_comparison_chart(self, results: List[SimulationResult], title: str, filename: str = "comparison.png"):
        """Plot comparison bar chart of different scenarios"""
        
        if not results:
            return
        
        scenarios = [r.scenario_name for r in results]
        times = [r.total_time_seconds / 60 for r in results]  # Convert to minutes
        speeds = [r.average_speed_kmh for r in results]
        
        # Reference time (fastest)
        ref_time = min(times)
        time_diffs = [(t - ref_time) for t in times]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Time comparison
        colors = ['green' if diff == 0 else 'red' if diff > 0 else 'blue' for diff in time_diffs]
        bars1 = ax1.bar(scenarios, times, color=colors, alpha=0.7)
        ax1.set_ylabel('Total Time (minutes)', fontsize=12)
        ax1.set_title('Total Time Comparison', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add time difference labels on bars
        for bar, diff in zip(bars1, time_diffs):
            height = bar.get_height()
            label = f"+{diff:.1f}min" if diff > 0 else f"{diff:.1f}min" if diff < 0 else "Fastest"
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    label, ha='center', va='bottom', fontweight='bold')
        
        # Speed comparison
        bars2 = ax2.bar(scenarios, speeds, color='blue', alpha=0.7)
        ax2.set_ylabel('Average Speed (km/h)', fontsize=12)
        ax2.set_title('Average Speed Comparison', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add speed labels on bars
        for bar, speed in zip(bars2, speeds):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f"{speed:.1f}", ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Comparison chart saved: {filename}")
        
        if self.show_plots:
            plt.show()
        else:
            plt.close()
    
    def plot_power_analysis(self, course: Course, result: SimulationResult, filename: str = "power_analysis.png"):
        """Plot power breakdown analysis"""
        
        # This is a simplified visualization - in reality we'd need to calculate 
        # aerodynamic, rolling, and climbing power for each segment
        
        climbs = course.get_climbing_segments(min_gradient=2.0)
        flats = course.get_flat_segments(gradient_tolerance=2.0)
        descents = course.get_descent_segments(max_gradient=-2.0)
        
        # Calculate approximate power distribution
        climb_distance = sum(seg.distance_m for seg in climbs) / 1000
        flat_distance = sum(seg.distance_m for seg in flats) / 1000
        descent_distance = sum(seg.distance_m for seg in descents) / 1000
        
        distances = [climb_distance, flat_distance, descent_distance]
        labels = ['Climbing', 'Flat', 'Descending']
        colors = ['red', 'green', 'blue']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Distance breakdown pie chart
        ax1.pie(distances, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Course Profile Breakdown', fontweight='bold')
        
        # Power requirements estimation (simplified)
        rider_weight = result.rider_config.rider.weight_kg
        bike_weight = 8.0  # Assume standard bike weight
        total_weight = rider_weight + bike_weight
        
        # Rough power estimates for different terrain
        climb_power = result.average_power_watts * 1.3  # Higher on climbs
        flat_power = result.average_power_watts * 0.9   # Lower on flats  
        descent_power = result.average_power_watts * 0.3 # Much lower on descents
        
        powers = [climb_power, flat_power, descent_power]
        
        bars = ax2.bar(labels, powers, color=colors, alpha=0.7)
        ax2.set_ylabel('Estimated Power (W)', fontsize=12)
        ax2.set_title('Power by Terrain Type', fontweight='bold')
        
        # Add power labels
        for bar, power in zip(bars, powers):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f"{power:.0f}W", ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if self.save_plots:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Power analysis saved: {filename}")
        
        if self.show_plots:
            plt.show()
        else:
            plt.close()