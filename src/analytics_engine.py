"""Analytics engine for traffic insights and visualizations.

This module provides the AnalyticsEngine class for generating
traffic analytics including object counts, time profiles, heatmaps,
and comparative statistics.
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from pathlib import Path
from models import Detection


logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Generates traffic analytics and visualizations.
    
    This class processes detection data to create various analytics
    including object counts, temporal patterns, spatial heatmaps,
    and comparative statistics between videos.
    
    Attributes:
        output_dir: Directory for saving visualizations
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """Initialize AnalyticsEngine with output directory.
        
        Args:
            output_dir: Directory where visualizations will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        logger.info(f"AnalyticsEngine initialized with output directory: {output_dir}")
    
    def compute_object_counts(self, detections: List[Detection]) -> Dict[str, int]:
        """Compute total object counts by class.
        
        Args:
            detections: List of Detection objects
            
        Returns:
            Dictionary mapping class names to counts
        """
        counts = {}
        
        for detection in detections:
            class_name = detection.class_name
            counts[class_name] = counts.get(class_name, 0) + 1
        
        # Add total count
        counts['total'] = len(detections)
        
        logger.info(f"Computed object counts: {counts}")
        return counts
    
    def generate_time_profile(self, detections: List[Detection], 
                             interval_seconds: int = 5) -> pd.DataFrame:
        """Generate time profile showing object counts over time.
        
        Args:
            detections: List of Detection objects
            interval_seconds: Time interval for aggregation (default: 5 seconds)
            
        Returns:
            DataFrame with time intervals and counts per class
        """
        if not detections:
            logger.warning("No detections provided for time profile")
            return pd.DataFrame()
        
        # Create DataFrame from detections
        data = []
        for det in detections:
            data.append({
                'timestamp': det.timestamp,
                'class_name': det.class_name
            })
        
        df = pd.DataFrame(data)
        
        # Create time bins
        max_time = df['timestamp'].max()
        bins = np.arange(0, max_time + interval_seconds, interval_seconds)
        df['time_bin'] = pd.cut(df['timestamp'], bins=bins, labels=bins[:-1], include_lowest=True)
        
        # Count objects per time bin and class
        time_profile = df.groupby(['time_bin', 'class_name']).size().unstack(fill_value=0)
        
        # Add total column
        time_profile['total'] = time_profile.sum(axis=1)
        
        # Reset index to make time_bin a column
        time_profile = time_profile.reset_index()
        time_profile['time_bin'] = time_profile['time_bin'].astype(float)
        
        logger.info(f"Generated time profile with {len(time_profile)} intervals")
        return time_profile
    
    def generate_heatmap(self, detections: List[Detection], 
                        frame_shape: Tuple[int, int],
                        grid_size: int = 50) -> np.ndarray:
        """Generate spatial heatmap of detection centers.
        
        Args:
            detections: List of Detection objects
            frame_shape: Video frame shape as (height, width)
            grid_size: Size of heatmap grid cells (default: 50 pixels)
            
        Returns:
            2D numpy array representing the heatmap
        """
        if not detections:
            logger.warning("No detections provided for heatmap")
            return np.zeros((10, 10))
        
        height, width = frame_shape
        
        # Calculate grid dimensions
        grid_height = (height + grid_size - 1) // grid_size
        grid_width = (width + grid_size - 1) // grid_size
        
        # Initialize heatmap
        heatmap = np.zeros((grid_height, grid_width))
        
        # Accumulate detection centers
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            
            # Calculate center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Map to grid coordinates
            grid_x = min(center_x // grid_size, grid_width - 1)
            grid_y = min(center_y // grid_size, grid_height - 1)
            
            # Increment heatmap
            heatmap[grid_y, grid_x] += 1
        
        logger.info(f"Generated heatmap with shape {heatmap.shape}")
        return heatmap
    
    def compare_videos(self, video1_stats: Dict, video2_stats: Dict) -> pd.DataFrame:
        """Generate comparative statistics between two videos.
        
        Args:
            video1_stats: Statistics dictionary for first video
            video2_stats: Statistics dictionary for second video
            
        Returns:
            DataFrame with comparative statistics
        """
        # Extract video names
        video1_name = video1_stats.get('video_name', 'Video 1')
        video2_name = video2_stats.get('video_name', 'Video 2')
        
        # Extract counts
        video1_counts = video1_stats.get('object_counts', {})
        video2_counts = video2_stats.get('object_counts', {})
        
        # Get all unique classes
        all_classes = set(video1_counts.keys()) | set(video2_counts.keys())
        all_classes.discard('total')  # Handle total separately
        
        # Build comparison data
        comparison_data = []
        
        for class_name in sorted(all_classes):
            count1 = video1_counts.get(class_name, 0)
            count2 = video2_counts.get(class_name, 0)
            difference = count2 - count1
            
            if count1 > 0:
                percent_change = (difference / count1) * 100
            else:
                percent_change = 100.0 if count2 > 0 else 0.0
            
            comparison_data.append({
                'class': class_name,
                video1_name: count1,
                video2_name: count2,
                'difference': difference,
                'percent_change': percent_change
            })
        
        # Add total row
        total1 = video1_counts.get('total', 0)
        total2 = video2_counts.get('total', 0)
        total_diff = total2 - total1
        total_pct = (total_diff / total1 * 100) if total1 > 0 else 0.0
        
        comparison_data.append({
            'class': 'TOTAL',
            video1_name: total1,
            video2_name: total2,
            'difference': total_diff,
            'percent_change': total_pct
        })
        
        df = pd.DataFrame(comparison_data)
        
        logger.info(f"Generated comparison between {video1_name} and {video2_name}")
        return df
    
    def plot_object_counts(self, counts: Dict[str, int], 
                          title: str = "Object Counts",
                          filename: str = "object_counts.png") -> Path:
        """Create bar plot of object counts.
        
        Args:
            counts: Dictionary of class names to counts
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved plot
        """
        output_path = self.output_dir / filename
        
        # Remove 'total' from counts for plotting
        plot_counts = {k: v for k, v in counts.items() if k != 'total'}
        
        if not plot_counts:
            logger.warning("No data to plot")
            return None
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        classes = list(plot_counts.keys())
        values = list(plot_counts.values())
        
        bars = ax.bar(classes, values, color='steelblue', edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Object Class', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved object counts plot to {output_path}")
        return output_path
    
    def plot_time_profile(self, time_profile: pd.DataFrame,
                         title: str = "Traffic Over Time",
                         filename: str = "time_profile.png") -> Path:
        """Create line plot of traffic over time.
        
        Args:
            time_profile: DataFrame with time bins and counts
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved plot
        """
        output_path = self.output_dir / filename
        
        if time_profile.empty:
            logger.warning("No data to plot")
            return None
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each class
        for column in time_profile.columns:
            if column not in ['time_bin', 'total']:
                ax.plot(time_profile['time_bin'], time_profile[column], 
                       marker='o', label=column, linewidth=2)
        
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Object Count', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved time profile plot to {output_path}")
        return output_path
    
    def plot_heatmap(self, heatmap: np.ndarray,
                    title: str = "Detection Heatmap",
                    filename: str = "heatmap.png") -> Path:
        """Create heatmap visualization.
        
        Args:
            heatmap: 2D numpy array with detection counts
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved plot
        """
        output_path = self.output_dir / filename
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot heatmap
        im = ax.imshow(heatmap, cmap='hot', interpolation='bilinear', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Detection Count', fontsize=12)
        
        ax.set_xlabel('Horizontal Position', fontsize=12)
        ax.set_ylabel('Vertical Position', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved heatmap to {output_path}")
        return output_path
    
    def plot_comparison(self, comparison_df: pd.DataFrame,
                       filename: str = "comparison.png") -> Path:
        """Create comparison bar plot between two videos.
        
        Args:
            comparison_df: DataFrame with comparison statistics
            filename: Output filename
            
        Returns:
            Path to saved plot
        """
        output_path = self.output_dir / filename
        
        if comparison_df.empty:
            logger.warning("No data to plot")
            return None
        
        # Remove TOTAL row for plotting
        plot_df = comparison_df[comparison_df['class'] != 'TOTAL'].copy()
        
        if plot_df.empty:
            return None
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(plot_df))
        width = 0.35
        
        video1_col = [col for col in plot_df.columns if col not in ['class', 'difference', 'percent_change']][0]
        video2_col = [col for col in plot_df.columns if col not in ['class', 'difference', 'percent_change']][1]
        
        bars1 = ax.bar(x - width/2, plot_df[video1_col], width, label=video1_col, color='steelblue')
        bars2 = ax.bar(x + width/2, plot_df[video2_col], width, label=video2_col, color='coral')
        
        ax.set_xlabel('Object Class', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Video Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(plot_df['class'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved comparison plot to {output_path}")
        return output_path


def main():
    """Test the AnalyticsEngine with sample data."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("\n=== Testing AnalyticsEngine ===\n")
        
        # Initialize engine
        print("Initializing AnalyticsEngine...")
        engine = AnalyticsEngine(output_dir="outputs/test_analytics")
        
        # Create sample detections
        print("Creating sample detections...")
        sample_detections = []
        
        # Simulate detections over time
        for i in range(100):
            timestamp = i * 0.5  # Every 0.5 seconds
            class_name = ['car', 'truck', 'bus', 'motorcycle'][i % 4]
            
            detection = Detection(
                bbox=(100 + i*10, 200, 300 + i*10, 400),
                class_name=class_name,
                confidence=0.9,
                frame_number=i,
                timestamp=timestamp
            )
            sample_detections.append(detection)
        
        print(f"Created {len(sample_detections)} sample detections\n")
        
        # Compute object counts
        print("=== Computing Object Counts ===")
        counts = engine.compute_object_counts(sample_detections)
        for class_name, count in sorted(counts.items()):
            print(f"{class_name}: {count}")
        
        # Generate time profile
        print("\n=== Generating Time Profile ===")
        time_profile = engine.generate_time_profile(sample_detections, interval_seconds=5)
        print(f"Time profile shape: {time_profile.shape}")
        print(time_profile.head())
        
        # Generate heatmap
        print("\n=== Generating Heatmap ===")
        heatmap = engine.generate_heatmap(sample_detections, frame_shape=(1080, 1920))
        print(f"Heatmap shape: {heatmap.shape}")
        print(f"Max detection count in cell: {heatmap.max()}")
        
        # Create visualizations
        print("\n=== Creating Visualizations ===")
        engine.plot_object_counts(counts, title="Sample Object Counts")
        print("✅ Object counts plot created")
        
        engine.plot_time_profile(time_profile, title="Sample Time Profile")
        print("✅ Time profile plot created")
        
        engine.plot_heatmap(heatmap, title="Sample Heatmap")
        print("✅ Heatmap created")
        
        print(f"\n✅ AnalyticsEngine test completed!")
        print(f"All outputs saved to: {engine.output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
