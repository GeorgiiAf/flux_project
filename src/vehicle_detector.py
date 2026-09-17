"""Vehicle detection component using YOLO object detection.

This module provides the VehicleDetector class for detecting vehicles
in video frames using YOLOv8 from Ultralytics.
"""

import logging
import numpy as np
from typing import List, Set
from pathlib import Path
from ultralytics import YOLO
from models import Detection


logger = logging.getLogger(__name__)


class VehicleDetector:
    """Detects vehicles and traffic participants in frames using YOLO object detection.
    
    This class uses YOLOv8 to detect vehicles (cars, trucks, buses, motorcycles),
    cyclists (bicycle), and pedestrians (person) in video frames. It filters 
    detections by confidence threshold and class types.
    
    Attributes:
        model: YOLO model instance
        confidence_threshold: Minimum confidence for detections
        vehicle_classes: Set of vehicle class names to detect
    """
    
    # COCO dataset class names that represent vehicles and traffic participants
    VEHICLE_CLASS_NAMES = {
        'car', 'truck', 'bus', 'motorcycle', 'bicycle', 'person'
    }
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """Initialize VehicleDetector with YOLO model.
        
        Args:
            model_path: Path to YOLO model weights (default: yolov8n.pt for speed)
                       Options: yolov8n.pt (nano), yolov8s.pt (small), 
                               yolov8m.pt (medium), yolov8l.pt (large)
            confidence_threshold: Minimum confidence score for detections (0.0-1.0)
            
        Raises:
            ValueError: If confidence threshold is not between 0.0 and 1.0
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(f"Confidence threshold must be between 0.0 and 1.0, got {confidence_threshold}")
        
        self.confidence_threshold = confidence_threshold
        self.vehicle_classes = self.VEHICLE_CLASS_NAMES.copy()
        
        logger.info(f"Loading YOLO model: {model_path}")
        try:
            self.model = YOLO(model_path)
            logger.info(f"YOLO model loaded successfully")
            logger.info(f"Vehicle classes to detect: {', '.join(sorted(self.vehicle_classes))}")
            logger.info(f"Confidence threshold: {confidence_threshold}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, frame: np.ndarray, frame_number: int = 0, timestamp: float = 0.0) -> List[Detection]:
        """Detect vehicles in a frame.
        
        Args:
            frame: Input frame as numpy array (BGR format from OpenCV)
            frame_number: Frame number for metadata
            timestamp: Timestamp for metadata
            
        Returns:
            List of Detection objects for vehicles found in the frame
        """
        if frame is None or frame.size == 0:
            logger.warning("Empty frame provided to detector")
            return []
        
        try:
            # Run YOLO inference
            results = self.model(frame, verbose=False)
            
            detections = []
            
            # Process results
            for result in results:
                # Get boxes, classes, and confidences
                boxes = result.boxes
                
                if boxes is None or len(boxes) == 0:
                    continue
                
                for box in boxes:
                    # Extract detection information
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    # Filter by confidence threshold
                    if confidence < self.confidence_threshold:
                        continue
                    
                    # Filter by vehicle classes
                    if class_name not in self.vehicle_classes:
                        continue
                    
                    # Get bounding box coordinates (xyxy format)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox = (int(x1), int(y1), int(x2), int(y2))
                    
                    # Create Detection object
                    detection = Detection(
                        bbox=bbox,
                        class_name=class_name,
                        confidence=confidence,
                        frame_number=frame_number,
                        timestamp=timestamp
                    )
                    
                    detections.append(detection)
            
            logger.debug(f"Detected {len(detections)} vehicles in frame {frame_number}")
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection in frame {frame_number}: {e}")
            return []
    
    def get_supported_classes(self) -> List[str]:
        """Get list of supported vehicle classes.
        
        Returns:
            List of vehicle class names that can be detected
        """
        return sorted(list(self.vehicle_classes))
    
    def filter_vehicles(self, detections: List[Detection]) -> List[Detection]:
        """Filter detections to only include vehicles.
        
        This method is useful when processing detections from external sources.
        
        Args:
            detections: List of Detection objects
            
        Returns:
            List of Detection objects filtered to only vehicle classes
        """
        return [d for d in detections if d.class_name in self.vehicle_classes]


def main():
    """Test the VehicleDetector with a sample video frame."""
    import sys
    import cv2
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test with command line argument or default video
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "data/videos/Clip1_morning.mp4"
    
    try:
        print("\n=== Testing VehicleDetector ===\n")
        
        # Initialize detector
        print("Initializing YOLO detector...")
        detector = VehicleDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
        
        print(f"Supported vehicle classes: {', '.join(detector.get_supported_classes())}")
        
        # Read a test frame from video
        print(f"\nReading test frame from: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video file: {video_path}")
            return 1
        
        # Read first frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("Error: Could not read frame from video")
            return 1
        
        print(f"Frame shape: {frame.shape}")
        
        # Detect vehicles
        print("\nRunning vehicle detection...")
        detections = detector.detect(frame, frame_number=0, timestamp=0.0)
        
        print(f"\n=== Detection Results ===")
        print(f"Total vehicles detected: {len(detections)}")
        
        if detections:
            print("\nDetailed results:")
            for i, det in enumerate(detections, 1):
                print(f"{i}. {det.class_name.capitalize()}")
                print(f"   Confidence: {det.confidence:.3f}")
                print(f"   Bounding box: {det.bbox}")
                print()
            
            # Count by class
            class_counts = {}
            for det in detections:
                class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1
            
            print("Counts by class:")
            for class_name, count in sorted(class_counts.items()):
                print(f"  {class_name}: {count}")
        else:
            print("No vehicles detected in this frame.")
        
        print("\n✅ VehicleDetector test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
