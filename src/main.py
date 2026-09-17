"""Command-line interface for the Vehicle Compliance Monitor.

This module provides a CLI for running the vehicle compliance monitoring
pipeline from the command line.
"""

import argparse
import logging
import sys
from pathlib import Path

from models import PipelineConfig
from pipeline import Pipeline


def setup_logging(verbose: bool = False):
    """Configure logging for the application.
    
    Args:
        verbose: If True, set logging level to DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('vehicle_compliance_monitor.log')
        ]
    )


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Vehicle Compliance Monitor - AI-powered vehicle compliance checking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single video
  python src/main.py --video data/videos/Clip1_morning.mp4
  
  # Process multiple videos
  python src/main.py --video data/videos/Clip1_morning.mp4 data/videos/Clip2_day.mp4
  
  # Custom output directory and database
  python src/main.py --video data/videos/Clip1_morning.mp4 --output results --database data/custom_watchlist.csv
  
  # Adjust confidence thresholds
  python src/main.py --video data/videos/Clip1_morning.mp4 --vehicle-conf 0.6 --ocr-conf 0.8
  
  # Disable analytics
  python src/main.py --video data/videos/Clip1_morning.mp4 --no-analytics
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--video',
        type=str,
        nargs='+',
        required=True,
        help='Path(s) to video file(s) to process'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        default='data/watchlist.csv',
        help='Path to compliance database CSV file (default: data/watchlist.csv)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=5,
        help='Frame extraction rate in FPS (default: 5)'
    )
    
    parser.add_argument(
        '--vehicle-conf',
        type=float,
        default=0.5,
        help='Vehicle detection confidence threshold 0.0-1.0 (default: 0.5)'
    )
    
    parser.add_argument(
        '--plate-conf',
        type=float,
        default=0.6,
        help='License plate detection confidence threshold 0.0-1.0 (default: 0.6)'
    )
    
    parser.add_argument(
        '--ocr-conf',
        type=float,
        default=0.7,
        help='OCR confidence threshold 0.0-1.0 (default: 0.7)'
    )
    
    parser.add_argument(
        '--no-analytics',
        action='store_true',
        help='Disable analytics generation (faster processing)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        
    Returns:
        True if valid, False otherwise
    """
    # Check video files exist
    for video_path in args.video:
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}")
            return False
    
    # Check database exists
    if not Path(args.database).exists():
        print(f"Error: Database file not found: {args.database}")
        print(f"Please create a watchlist database at: {args.database}")
        return False
    
    # Validate confidence thresholds
    if not 0.0 <= args.vehicle_conf <= 1.0:
        print(f"Error: Vehicle confidence must be between 0.0 and 1.0, got {args.vehicle_conf}")
        return False
    
    if not 0.0 <= args.plate_conf <= 1.0:
        print(f"Error: Plate confidence must be between 0.0 and 1.0, got {args.plate_conf}")
        return False
    
    if not 0.0 <= args.ocr_conf <= 1.0:
        print(f"Error: OCR confidence must be between 0.0 and 1.0, got {args.ocr_conf}")
        return False
    
    # Validate FPS
    if args.fps <= 0:
        print(f"Error: FPS must be positive, got {args.fps}")
        return False
    
    return True


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           VEHICLE COMPLIANCE MONITOR                                 ║
║           AI-Powered Vehicle Compliance Checking System              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_configuration(config: PipelineConfig, video_paths: list):
    """Print configuration summary.
    
    Args:
        config: Pipeline configuration
        video_paths: List of video paths
    """
    print("\n" + "=" * 70)
    print("CONFIGURATION")
    print("=" * 70)
    print(f"Videos to process: {len(video_paths)}")
    for i, path in enumerate(video_paths, 1):
        print(f"  {i}. {path}")
    print(f"\nOutput directory: {config.output_dir}")
    print(f"Database: {config.database_path}")
    print(f"Frame extraction FPS: {config.frame_extraction_fps}")
    print(f"\nConfidence Thresholds:")
    print(f"  Vehicle detection: {config.vehicle_confidence_threshold}")
    print(f"  Plate detection: {config.plate_confidence_threshold}")
    print(f"  OCR: {config.ocr_confidence_threshold}")
    print(f"\nAnalytics: {'Enabled' if config.enable_analytics else 'Disabled'}")
    print("=" * 70 + "\n")


def main():
    """Main entry point for the CLI."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Print banner
    print_banner()
    
    # Validate arguments
    if not validate_arguments(args):
        return 1
    
    try:
        # Create configuration
        config = PipelineConfig(
            vehicle_confidence_threshold=args.vehicle_conf,
            plate_confidence_threshold=args.plate_conf,
            ocr_confidence_threshold=args.ocr_conf,
            frame_extraction_fps=args.fps,
            database_path=args.database,
            output_dir=args.output,
            enable_analytics=not args.no_analytics
        )
        
        # Print configuration
        print_configuration(config, args.video)
        
        # Initialize pipeline
        print("Initializing pipeline components...")
        pipeline = Pipeline(config)
        print("✓ Pipeline initialized\n")
        
        # Process videos
        if len(args.video) == 1:
            # Single video
            print(f"Processing single video: {args.video[0]}\n")
            result = pipeline.process_video(args.video[0])
            
        else:
            # Multiple videos
            print(f"Processing {len(args.video)} videos in batch\n")
            results = pipeline.process_batch(args.video)
        
        # Success message
        print("\n" + "=" * 70)
        print("✓ PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nAll outputs saved to: {config.output_dir}/")
        print("\nGenerated files:")
        print("  - Violation reports (CSV, JSON, TXT)")
        if config.enable_analytics:
            print("  - Analytics visualizations (PNG)")
            print("  - Time profiles and heatmaps")
            if len(args.video) > 1:
                print("  - Video comparison analysis")
        print("  - Annotated videos (if violations found)")
        print("\n" + "=" * 70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        print("Partial results may have been saved to output directory")
        return 130
        
    except Exception as e:
        print(f"\n\nError: {e}")
        logging.exception("Fatal error during processing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
