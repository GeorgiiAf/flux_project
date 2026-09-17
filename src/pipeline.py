"""Main pipeline orchestrator for the Vehicle Compliance Monitor.

This module provides the Pipeline class that coordinates all components
to process videos end-to-end.
"""

import logging
import cv2
from typing import List, Dict
from pathlib import Path
from tqdm import tqdm

from models import PipelineConfig, ViolationRecord
from video_processor import VideoProcessor
from vehicle_detector import VehicleDetector
from plate_detector import LicensePlateDetector
from ocr_engine import OCREngine
from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator
from analytics_engine import AnalyticsEngine


logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the complete vehicle compliance monitoring pipeline.
    
    This class coordinates all components to process videos from start to finish:
    1. Extract frames from video
    2. Detect vehicles in each frame
    3. Detect license plates in vehicles
    4. Run OCR on plates
    5. Check plates against compliance database
    6. Generate violation records
    7. Create analytics and visualizations
    8. Export all outputs
    
    Attributes:
        config: Pipeline configuration
        video_processor: VideoProcessor instance
        vehicle_detector: VehicleDetector instance
        plate_detector: LicensePlateDetector instance
        ocr_engine: OCREngine instance
        compliance_checker: ComplianceChecker instance
        report_generator: ReportGenerator instance
        analytics_engine: AnalyticsEngine instance
    """
    
    def __init__(self, config: PipelineConfig):
        """Initialize Pipeline with configuration.
        
        Args:
            config: PipelineConfig object with all settings
        """
        self.config = config
        
        logger.info("Initializing pipeline components...")
        
        # Initialize all components
        try:
            self.vehicle_detector = VehicleDetector(
                confidence_threshold=config.vehicle_confidence_threshold
            )
            logger.info("✓ VehicleDetector initialized")
            
            self.plate_detector = LicensePlateDetector(
                confidence_threshold=config.plate_confidence_threshold
            )
            logger.info("✓ LicensePlateDetector initialized")
            
            self.ocr_engine = OCREngine(
                confidence_threshold=config.ocr_confidence_threshold
            )
            logger.info("✓ OCREngine initialized")
            
            self.compliance_checker = ComplianceChecker(
                database_path=config.database_path
            )
            logger.info("✓ ComplianceChecker initialized")
            
            self.report_generator = ReportGenerator(
                output_dir=config.output_dir
            )
            logger.info("✓ ReportGenerator initialized")
            
            if config.enable_analytics:
                self.analytics_engine = AnalyticsEngine(
                    output_dir=config.output_dir
                )
                logger.info("✓ AnalyticsEngine initialized")
            else:
                self.analytics_engine = None
            
            logger.info("Pipeline initialization complete!")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise
    
    def process_video(self, video_path: str) -> Dict:
        """Process a single video through the complete pipeline.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with processing results and statistics
        """
        video_path = Path(video_path)
        logger.info(f"=" * 80)
        logger.info(f"Processing video: {video_path.name}")
        logger.info(f"=" * 80)
        
        # Initialize video processor
        video_processor = VideoProcessor(
            video_path=str(video_path),
            fps=self.config.frame_extraction_fps
        )
        
        # Get video metadata
        video_metadata = video_processor.get_video_info()
        logger.info(f"Video: {video_metadata.resolution[0]}x{video_metadata.resolution[1]}, "
                   f"{video_metadata.duration:.2f}s, {video_metadata.fps:.2f} fps")
        
        # Storage for detections and statistics
        all_detections = []
        frame_count = 0
        vehicle_count = 0
        plate_detected_count = 0
        ocr_success_count = 0
        violation_count = 0
        
        # Process frames
        logger.info("Processing frames...")
        
        try:
            for frame in tqdm(video_processor.extract_frames(), 
                            desc="Processing frames",
                            unit="frame"):
                frame_count += 1
                
                # Step 1: Detect vehicles
                detections = self.vehicle_detector.detect(
                    frame.image,
                    frame_number=frame.frame_number,
                    timestamp=frame.timestamp
                )
                
                vehicle_count += len(detections)
                all_detections.extend(detections)
                
                # Step 2-5: Process each detected vehicle
                for detection in detections:
                    # Extract vehicle crop
                    x1, y1, x2, y2 = detection.bbox
                    vehicle_crop = frame.image[y1:y2, x1:x2]
                    
                    if vehicle_crop.size == 0:
                        continue
                    
                    # Step 2: Detect license plate
                    plate_region = self.plate_detector.detect_plate(vehicle_crop)
                    
                    if plate_region is None:
                        continue
                    
                    plate_detected_count += 1
                    
                    # Extract plate crop
                    px1, py1, px2, py2 = plate_region.bbox
                    plate_crop = vehicle_crop[py1:py2, px1:px2]
                    
                    if plate_crop.size == 0:
                        continue
                    
                    # Step 3: Run OCR
                    plate_reading = self.ocr_engine.read_plate(plate_crop)
                    
                    if plate_reading is None:
                        continue
                    
                    ocr_success_count += 1
                    
                    # Step 4: Check compliance
                    violation_info = self.compliance_checker.check_plate(plate_reading.text)
                    
                    if violation_info is None:
                        continue
                    
                    # Step 5: Create violation record
                    violation_record = ViolationRecord(
                        plate_number=plate_reading.text,
                        violation_category=violation_info.category,
                        frame_number=frame.frame_number,
                        timestamp=frame.timestamp,
                        video_source=video_metadata.filename,
                        detection_confidence=detection.confidence,
                        ocr_confidence=plate_reading.confidence,
                        bbox=detection.bbox
                    )
                    
                    self.report_generator.add_violation(violation_record)
                    violation_count += 1
                    
                    logger.info(f"VIOLATION DETECTED: {plate_reading.text} - {violation_info.category} "
                              f"at {frame.timestamp:.2f}s")
        
        except Exception as e:
            logger.error(f"Error during frame processing: {e}")
            logger.info("Saving partial results...")
        
        # Generate reports
        logger.info("\nGenerating reports...")
        
        csv_path = self.report_generator.export_csv(
            filename=f"violations_{video_path.stem}.csv"
        )
        logger.info(f"✓ CSV report: {csv_path}")
        
        json_path = self.report_generator.export_json(
            filename=f"violations_{video_path.stem}.json"
        )
        logger.info(f"✓ JSON report: {json_path}")
        
        summary_path = self.report_generator.generate_summary_report(
            filename=f"summary_{video_path.stem}.txt"
        )
        logger.info(f"✓ Summary report: {summary_path}")
        
        # Generate annotated video if violations found
        if violation_count > 0:
            logger.info("Generating annotated video...")
            annotated_path = self.report_generator.generate_annotated_video(
                video_path=str(video_path),
                output_filename=f"annotated_{video_path.name}"
            )
            if annotated_path:
                logger.info(f"✓ Annotated video: {annotated_path}")
        
        # Generate analytics
        analytics_results = {}
        
        if self.config.enable_analytics and all_detections:
            logger.info("\nGenerating analytics...")
            
            # Object counts
            object_counts = self.analytics_engine.compute_object_counts(all_detections)
            analytics_results['object_counts'] = object_counts
            
            self.analytics_engine.plot_object_counts(
                object_counts,
                title=f"Object Counts - {video_path.stem}",
                filename=f"counts_{video_path.stem}.png"
            )
            logger.info("✓ Object counts plot")
            
            # Time profile
            time_profile = self.analytics_engine.generate_time_profile(
                all_detections,
                interval_seconds=5
            )
            analytics_results['time_profile'] = time_profile
            
            # Save time profile to CSV
            time_profile_path = Path(self.config.output_dir) / f"time_profile_{video_path.stem}.csv"
            time_profile.to_csv(time_profile_path, index=False)
            logger.info(f"✓ Time profile CSV: {time_profile_path}")
            
            self.analytics_engine.plot_time_profile(
                time_profile,
                title=f"Traffic Over Time - {video_path.stem}",
                filename=f"time_profile_{video_path.stem}.png"
            )
            logger.info("✓ Time profile plot")
            
            # Heatmap
            heatmap = self.analytics_engine.generate_heatmap(
                all_detections,
                frame_shape=(video_metadata.resolution[1], video_metadata.resolution[0])
            )
            analytics_results['heatmap'] = heatmap
            
            self.analytics_engine.plot_heatmap(
                heatmap,
                title=f"Detection Heatmap - {video_path.stem}",
                filename=f"heatmap_{video_path.stem}.png"
            )
            logger.info("✓ Heatmap")
        
        # Summary statistics
        logger.info("\n" + "=" * 80)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Frames processed: {frame_count}")
        logger.info(f"Vehicles detected: {vehicle_count}")
        logger.info(f"Plates detected: {plate_detected_count}")
        logger.info(f"OCR successful: {ocr_success_count}")
        logger.info(f"Violations found: {violation_count}")
        logger.info("=" * 80)
        
        # Return results
        return {
            'video_name': video_path.name,
            'video_metadata': video_metadata,
            'frames_processed': frame_count,
            'vehicles_detected': vehicle_count,
            'plates_detected': plate_detected_count,
            'ocr_successful': ocr_success_count,
            'violations_found': violation_count,
            'object_counts': analytics_results.get('object_counts', {}),
            'analytics': analytics_results
        }
    
    def process_batch(self, video_paths: List[str]) -> List[Dict]:
        """Process multiple videos in batch.
        
        Args:
            video_paths: List of paths to video files
            
        Returns:
            List of result dictionaries, one per video
        """
        logger.info(f"Processing batch of {len(video_paths)} videos")
        
        results = []
        
        for video_path in video_paths:
            try:
                result = self.process_video(video_path)
                results.append(result)
                
                # Clear violations for next video
                self.report_generator.clear_violations()
                
            except Exception as e:
                logger.error(f"Failed to process {video_path}: {e}")
                results.append({
                    'video_name': Path(video_path).name,
                    'error': str(e)
                })
        
        # Generate comparative analytics if multiple videos processed successfully
        if len(results) >= 2 and self.config.enable_analytics:
            logger.info("\nGenerating comparative analytics...")
            
            # Compare first two videos
            comparison_df = self.analytics_engine.compare_videos(
                results[0],
                results[1]
            )
            
            # Save comparison
            comparison_path = Path(self.config.output_dir) / "video_comparison.csv"
            comparison_df.to_csv(comparison_path, index=False)
            logger.info(f"✓ Comparison CSV: {comparison_path}")
            
            self.analytics_engine.plot_comparison(
                comparison_df,
                filename="video_comparison.png"
            )
            logger.info("✓ Comparison plot")
        
        logger.info(f"\nBatch processing complete: {len(results)} videos processed")
        
        return results


def main():
    """Test the Pipeline with sample configuration."""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("\n" + "=" * 80)
        print("VEHICLE COMPLIANCE MONITOR - PIPELINE TEST")
        print("=" * 80 + "\n")
        
        # Create configuration
        config = PipelineConfig(
            vehicle_confidence_threshold=0.5,
            plate_confidence_threshold=0.6,
            ocr_confidence_threshold=0.7,
            frame_extraction_fps=5,
            database_path="data/watchlist.csv",
            output_dir="outputs",
            enable_analytics=True
        )
        
        print("Configuration:")
        print(f"  Vehicle confidence: {config.vehicle_confidence_threshold}")
        print(f"  Plate confidence: {config.plate_confidence_threshold}")
        print(f"  OCR confidence: {config.ocr_confidence_threshold}")
        print(f"  Frame extraction FPS: {config.frame_extraction_fps}")
        print(f"  Database: {config.database_path}")
        print(f"  Output directory: {config.output_dir}")
        print(f"  Analytics enabled: {config.enable_analytics}")
        print()
        
        # Initialize pipeline
        print("Initializing pipeline...")
        pipeline = Pipeline(config)
        print()
        
        # Get video paths
        if len(sys.argv) > 1:
            video_paths = sys.argv[1:]
        else:
            # Default to test videos
            video_paths = [
                "data/videos/Clip1_morning.mp4",
                "data/videos/Clip2_day.mp4"
            ]
        
        # Filter existing videos
        existing_videos = [v for v in video_paths if Path(v).exists()]
        
        if not existing_videos:
            print("No video files found!")
            print("Usage: python src/pipeline.py <video1> [video2] ...")
            return 1
        
        print(f"Videos to process: {len(existing_videos)}")
        for v in existing_videos:
            print(f"  - {v}")
        print()
        
        # Process videos
        if len(existing_videos) == 1:
            results = pipeline.process_video(existing_videos[0])
        else:
            results = pipeline.process_batch(existing_videos)
        
        print("\n" + "=" * 80)
        print("PIPELINE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nCheck outputs in: {config.output_dir}/")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
