"""Report generation component for violation records.

This module provides the ReportGenerator class for creating
violation reports in various formats and generating annotated videos.
"""

import logging
import json
import cv2
import pandas as pd
from typing import List
from pathlib import Path
from models import ViolationRecord


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates violation reports and annotated videos.
    
    This class accumulates violation records and exports them to
    structured formats (CSV, JSON) and creates annotated videos
    showing detected violations.
    
    Attributes:
        output_dir: Directory for output files
        violations: List of accumulated violation records
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """Initialize ReportGenerator with output directory.
        
        Args:
            output_dir: Directory where output files will be saved
        """
        self.output_dir = Path(output_dir)
        self.violations: List[ViolationRecord] = []
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ReportGenerator initialized with output directory: {output_dir}")
    
    def add_violation(self, violation: ViolationRecord):
        """Add a violation record to the report.
        
        Args:
            violation: ViolationRecord object to add
        """
        self.violations.append(violation)
        logger.debug(f"Added violation: {violation.plate_number} ({violation.violation_category})")
    
    def export_csv(self, filename: str = "violations.csv") -> Path:
        """Export violations to CSV file.
        
        Args:
            filename: Output filename (default: violations.csv)
            
        Returns:
            Path to the created CSV file
        """
        output_path = self.output_dir / filename
        
        if not self.violations:
            logger.warning("No violations to export")
            # Create empty CSV with headers
            df = pd.DataFrame(columns=[
                'plate_number', 'violation_category', 'frame_number', 
                'timestamp', 'video_source', 'detection_confidence', 
                'ocr_confidence', 'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2'
            ])
        else:
            # Convert violations to DataFrame
            data = []
            for v in self.violations:
                data.append({
                    'plate_number': v.plate_number,
                    'violation_category': v.violation_category,
                    'frame_number': v.frame_number,
                    'timestamp': v.timestamp,
                    'video_source': v.video_source,
                    'detection_confidence': v.detection_confidence,
                    'ocr_confidence': v.ocr_confidence,
                    'bbox_x1': v.bbox[0],
                    'bbox_y1': v.bbox[1],
                    'bbox_x2': v.bbox[2],
                    'bbox_y2': v.bbox[3]
                })
            
            df = pd.DataFrame(data)
        
        # Export to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(self.violations)} violations to {output_path}")
        
        return output_path
    
    def export_json(self, filename: str = "violations.json") -> Path:
        """Export violations to JSON file.
        
        Args:
            filename: Output filename (default: violations.json)
            
        Returns:
            Path to the created JSON file
        """
        output_path = self.output_dir / filename
        
        # Convert violations to dictionaries
        data = []
        for v in self.violations:
            data.append({
                'plate_number': v.plate_number,
                'violation_category': v.violation_category,
                'frame_number': v.frame_number,
                'timestamp': v.timestamp,
                'video_source': v.video_source,
                'detection_confidence': v.detection_confidence,
                'ocr_confidence': v.ocr_confidence,
                'bbox': {
                    'x1': v.bbox[0],
                    'y1': v.bbox[1],
                    'x2': v.bbox[2],
                    'y2': v.bbox[3]
                }
            })
        
        # Export to JSON
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(self.violations)} violations to {output_path}")
        
        return output_path
    
    def generate_summary_report(self, filename: str = "summary.txt") -> Path:
        """Generate a human-readable summary report.
        
        Args:
            filename: Output filename (default: summary.txt)
            
        Returns:
            Path to the created summary file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("VEHICLE COMPLIANCE MONITORING REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            if not self.violations:
                f.write("No violations detected.\n")
            else:
                f.write(f"Total Violations: {len(self.violations)}\n\n")
                
                # Count by category
                categories = {}
                for v in self.violations:
                    categories[v.violation_category] = categories.get(v.violation_category, 0) + 1
                
                f.write("Violations by Category:\n")
                for category, count in sorted(categories.items()):
                    f.write(f"  {category}: {count}\n")
                
                f.write("\n" + "-" * 60 + "\n\n")
                f.write("Detailed Violations:\n\n")
                
                for i, v in enumerate(self.violations, 1):
                    f.write(f"{i}. Plate: {v.plate_number}\n")
                    f.write(f"   Category: {v.violation_category}\n")
                    f.write(f"   Video: {v.video_source}\n")
                    f.write(f"   Time: {v.timestamp:.2f}s (frame {v.frame_number})\n")
                    f.write(f"   Confidence: Detection={v.detection_confidence:.3f}, OCR={v.ocr_confidence:.3f}\n")
                    f.write("\n")
        
        logger.info(f"Generated summary report: {output_path}")
        return output_path
    
    def generate_annotated_video(self, video_path: str, output_filename: str = None) -> Path:
        """Generate annotated video with bounding boxes around violations.
        
        Args:
            video_path: Path to the original video file
            output_filename: Output filename (default: annotated_{original_name}.mp4)
            
        Returns:
            Path to the created annotated video
        """
        video_path = Path(video_path)
        
        if output_filename is None:
            output_filename = f"annotated_{video_path.name}"
        
        output_path = self.output_dir / output_filename
        
        # Filter violations for this video
        video_violations = [v for v in self.violations if v.video_source == video_path.name]
        
        if not video_violations:
            logger.warning(f"No violations found for video: {video_path.name}")
            return None
        
        logger.info(f"Generating annotated video for {len(video_violations)} violations")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Create frame-to-violations mapping
        frame_violations = {}
        for v in video_violations:
            if v.frame_number not in frame_violations:
                frame_violations[v.frame_number] = []
            frame_violations[v.frame_number].append(v)
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Check if this frame has violations
                if frame_count in frame_violations:
                    for violation in frame_violations[frame_count]:
                        # Draw bounding box
                        x1, y1, x2, y2 = violation.bbox
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        
                        # Add label
                        label = f"{violation.plate_number} - {violation.violation_category}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        
                        # Draw label background
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 0, 255), -1)
                        
                        # Draw label text
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Write frame
                out.write(frame)
                frame_count += 1
            
            logger.info(f"Annotated video created: {output_path}")
            
        finally:
            cap.release()
            out.release()
        
        return output_path
    
    def clear_violations(self):
        """Clear all accumulated violations."""
        self.violations.clear()
        logger.info("Cleared all violations")
    
    def get_violation_count(self) -> int:
        """Get the number of accumulated violations.
        
        Returns:
            Number of violations
        """
        return len(self.violations)


def main():
    """Test the ReportGenerator with sample data."""
    from datetime import datetime
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("\n=== Testing ReportGenerator ===\n")
        
        # Initialize generator
        print("Initializing ReportGenerator...")
        generator = ReportGenerator(output_dir="outputs/test")
        
        # Create sample violations
        print("Creating sample violations...")
        sample_violations = [
            ViolationRecord(
                plate_number="ABC123",
                violation_category="expired_inspection",
                frame_number=100,
                timestamp=20.0,
                video_source="test_video.mp4",
                detection_confidence=0.95,
                ocr_confidence=0.88,
                bbox=(100, 200, 300, 400)
            ),
            ViolationRecord(
                plate_number="XYZ789",
                violation_category="stolen",
                frame_number=250,
                timestamp=50.0,
                video_source="test_video.mp4",
                detection_confidence=0.92,
                ocr_confidence=0.85,
                bbox=(150, 250, 350, 450)
            ),
            ViolationRecord(
                plate_number="DEF456",
                violation_category="blacklisted",
                frame_number=400,
                timestamp=80.0,
                video_source="test_video.mp4",
                detection_confidence=0.89,
                ocr_confidence=0.91,
                bbox=(200, 300, 400, 500)
            ),
        ]
        
        # Add violations
        for violation in sample_violations:
            generator.add_violation(violation)
        
        print(f"Added {generator.get_violation_count()} violations\n")
        
        # Export to CSV
        print("=== Exporting to CSV ===")
        csv_path = generator.export_csv("test_violations.csv")
        print(f"✅ CSV exported to: {csv_path}\n")
        
        # Export to JSON
        print("=== Exporting to JSON ===")
        json_path = generator.export_json("test_violations.json")
        print(f"✅ JSON exported to: {json_path}\n")
        
        # Generate summary
        print("=== Generating Summary Report ===")
        summary_path = generator.generate_summary_report("test_summary.txt")
        print(f"✅ Summary exported to: {summary_path}\n")
        
        # Display summary content
        print("Summary content:")
        print("-" * 60)
        with open(summary_path, 'r') as f:
            print(f.read())
        
        print("\n✅ ReportGenerator test completed!")
        print(f"\nAll outputs saved to: {generator.output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
