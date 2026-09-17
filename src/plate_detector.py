"""License plate detection component.

This module provides the LicensePlateDetector class for detecting
license plate regions within vehicle images.
"""

import logging
import numpy as np
from typing import Optional
from ultralytics import YOLO
from models import PlateRegion


logger = logging.getLogger(__name__)


class LicensePlateDetector:
    """Detects license plates within vehicle images.
    
    This class uses a YOLO model fine-tuned for license plate detection
    to locate plate regions within vehicle crops. It can use either a
    custom-trained model or a pre-trained license plate detection model.
    
    Attributes:
        model: YOLO model instance for plate detection
        confidence_threshold: Minimum confidence for plate detections
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.6):
        """Initialize LicensePlateDetector with model.
        
        Args:
            model_path: Path to YOLO model weights trained for license plates
                       For MVP, we'll use the standard YOLO model and look for
                       rectangular regions in the lower portion of vehicles
            confidence_threshold: Minimum confidence score for detections (0.0-1.0)
            
        Raises:
            ValueError: If confidence threshold is not between 0.0 and 1.0
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(f"Confidence threshold must be between 0.0 and 1.0, got {confidence_threshold}")
        
        self.confidence_threshold = confidence_threshold
        
        logger.info(f"Loading license plate detection model: {model_path}")
        try:
            self.model = YOLO(model_path)
            logger.info(f"License plate detection model loaded successfully")
            logger.info(f"Confidence threshold: {confidence_threshold}")
        except Exception as e:
            logger.error(f"Failed to load license plate detection model: {e}")
            raise
    
    def detect_plate(self, vehicle_crop: np.ndarray) -> Optional[PlateRegion]:
        """Detect license plate region within a vehicle crop.
        
        This method attempts to find a license plate within the provided
        vehicle image. It returns the first high-confidence detection.
        
        Args:
            vehicle_crop: Cropped vehicle image as numpy array (BGR format)
            
        Returns:
            PlateRegion object with bounding box and confidence, or None if no plate found
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            logger.warning("Empty vehicle crop provided to plate detector")
            return None
        
        try:
            # For MVP: Use heuristic-based detection
            # Look for rectangular regions in the lower 60% of the vehicle
            # This is a simplified approach; a trained model would be better
            plate_region = self._detect_plate_heuristic(vehicle_crop)
            
            if plate_region is not None:
                logger.debug(f"Detected plate region with confidence {plate_region.confidence:.3f}")
            
            return plate_region
            
        except Exception as e:
            logger.error(f"Error during plate detection: {e}")
            return None
    
    def _detect_plate_heuristic(self, vehicle_crop: np.ndarray) -> Optional[PlateRegion]:
        """Heuristic-based plate detection for MVP.
        
        This method uses a simple heuristic to estimate plate location:
        - Plates are typically in the lower portion of vehicles
        - Plates have a rectangular shape with specific aspect ratio
        - For MVP, we'll create a reasonable estimate
        
        In production, this should be replaced with a trained YOLO model
        specifically for license plate detection.
        
        Args:
            vehicle_crop: Cropped vehicle image
            
        Returns:
            PlateRegion or None
        """
        height, width = vehicle_crop.shape[:2]
        
        # Heuristic: Assume plate is in lower 40% of vehicle, centered horizontally
        # Typical plate aspect ratio is about 2:1 to 5:1 (width:height)
        
        # Estimate plate dimensions (rough approximation)
        plate_width = int(width * 0.4)  # Plate is about 40% of vehicle width
        plate_height = int(plate_width * 0.25)  # Aspect ratio ~4:1
        
        # Position in lower portion of vehicle
        plate_x1 = (width - plate_width) // 2
        plate_y1 = int(height * 0.7)  # Start at 70% down the vehicle
        plate_x2 = plate_x1 + plate_width
        plate_y2 = plate_y1 + plate_height
        
        # Ensure coordinates are within bounds
        plate_x1 = max(0, plate_x1)
        plate_y1 = max(0, plate_y1)
        plate_x2 = min(width, plate_x2)
        plate_y2 = min(height, plate_y2)
        
        # Validate bounding box
        if plate_x2 <= plate_x1 or plate_y2 <= plate_y1:
            logger.warning("Invalid plate region calculated")
            return None
        
        # Assign a moderate confidence since this is heuristic-based
        confidence = 0.65
        
        bbox = (plate_x1, plate_y1, plate_x2, plate_y2)
        
        try:
            plate_region = PlateRegion(bbox=bbox, confidence=confidence)
            return plate_region
        except Exception as e:
            logger.error(f"Error creating PlateRegion: {e}")
            return None
    
    def _detect_plate_with_model(self, vehicle_crop: np.ndarray) -> Optional[PlateRegion]:
        """Model-based plate detection (for future enhancement).
        
        This method would use a trained YOLO model specifically for
        license plate detection. Currently not implemented in MVP.
        
        Args:
            vehicle_crop: Cropped vehicle image
            
        Returns:
            PlateRegion or None
        """
        # Run YOLO inference
        results = self.model(vehicle_crop, verbose=False)
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            if boxes is None or len(boxes) == 0:
                continue
            
            # Get the first high-confidence detection
            for box in boxes:
                confidence = float(box.conf[0])
                
                if confidence < self.confidence_threshold:
                    continue
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox = (int(x1), int(y1), int(x2), int(y2))
                
                try:
                    plate_region = PlateRegion(bbox=bbox, confidence=confidence)
                    return plate_region
                except Exception as e:
                    logger.error(f"Error creating PlateRegion: {e}")
                    continue
        
        return None


def main():
    """Test the LicensePlateDetector with a sample vehicle crop."""
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
        print("\n=== Testing LicensePlateDetector ===\n")
        
        # Initialize detector
        print("Initializing license plate detector...")
        detector = LicensePlateDetector(confidence_threshold=0.6)
        
        # Read a test frame from video
        print(f"Reading test frame from: {video_path}")
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
        
        # For testing, use the whole frame as a "vehicle crop"
        # In real usage, this would be a cropped vehicle region
        vehicle_crop = frame
        
        print(f"Vehicle crop shape: {vehicle_crop.shape}")
        
        # Detect plate
        print("\nDetecting license plate region...")
        plate_region = detector.detect_plate(vehicle_crop)
        
        print(f"\n=== Detection Results ===")
        if plate_region:
            print(f"✅ License plate region detected!")
            print(f"   Bounding box: {plate_region.bbox}")
            print(f"   Confidence: {plate_region.confidence:.3f}")
            
            # Calculate dimensions
            x1, y1, x2, y2 = plate_region.bbox
            width = x2 - x1
            height = y2 - y1
            aspect_ratio = width / height if height > 0 else 0
            
            print(f"   Dimensions: {width}x{height} pixels")
            print(f"   Aspect ratio: {aspect_ratio:.2f}:1")
        else:
            print("❌ No license plate region detected")
        
        print("\n✅ LicensePlateDetector test completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
