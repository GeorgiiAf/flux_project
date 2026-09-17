"""Data models for the Vehicle Compliance Monitor system.

This module defines all the core data structures used throughout the pipeline,
including frames, detections, plate readings, violations, and configuration.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
import numpy as np


@dataclass
class Frame:
    """Represents a single video frame with metadata.
    
    Attributes:
        image: Frame image data as numpy array
        frame_number: Sequential frame index starting from 0
        timestamp: Time in seconds from video start
        video_source: Source video filename
    """
    image: np.ndarray
    frame_number: int
    timestamp: float
    video_source: str
    
    def __post_init__(self):
        """Validate frame data after initialization."""
        if self.frame_number < 0:
            raise ValueError(f"Frame number must be non-negative, got {self.frame_number}")
        if self.timestamp < 0:
            raise ValueError(f"Timestamp must be non-negative, got {self.timestamp}")
        if self.image is None or self.image.size == 0:
            raise ValueError("Frame image cannot be empty")


@dataclass
class Detection:
    """Represents a detected object in a frame.
    
    Attributes:
        bbox: Bounding box as (x1, y1, x2, y2) coordinates
        class_name: Object class (e.g., "car", "truck", "bus")
        confidence: Detection confidence score between 0.0 and 1.0
        frame_number: Frame number where detection occurred
        timestamp: Time in video when detection occurred
    """
    bbox: Tuple[int, int, int, int]
    class_name: str
    confidence: float
    frame_number: int
    timestamp: float
    
    def __post_init__(self):
        """Validate detection data after initialization."""
        # Validate bounding box
        x1, y1, x2, y2 = self.bbox
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            raise ValueError(f"Bounding box coordinates must be non-negative, got {self.bbox}")
        if x2 <= x1:
            raise ValueError(f"x2 must be greater than x1, got x1={x1}, x2={x2}")
        if y2 <= y1:
            raise ValueError(f"y2 must be greater than y1, got y1={y1}, y2={y2}")
        
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Validate frame number and timestamp
        if self.frame_number < 0:
            raise ValueError(f"Frame number must be non-negative, got {self.frame_number}")
        if self.timestamp < 0:
            raise ValueError(f"Timestamp must be non-negative, got {self.timestamp}")


@dataclass
class PlateRegion:
    """Represents a detected license plate region within a vehicle.
    
    Attributes:
        bbox: Bounding box relative to vehicle crop as (x1, y1, x2, y2)
        confidence: Detection confidence score between 0.0 and 1.0
    """
    bbox: Tuple[int, int, int, int]
    confidence: float
    
    def __post_init__(self):
        """Validate plate region data after initialization."""
        # Validate bounding box
        x1, y1, x2, y2 = self.bbox
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            raise ValueError(f"Bounding box coordinates must be non-negative, got {self.bbox}")
        if x2 <= x1:
            raise ValueError(f"x2 must be greater than x1, got x1={x1}, x2={x2}")
        if y2 <= y1:
            raise ValueError(f"y2 must be greater than y1, got y1={y1}, y2={y2}")
        
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class PlateReading:
    """Represents an OCR reading of a license plate.
    
    Attributes:
        text: Normalized plate number (uppercase, no spaces)
        confidence: OCR confidence score between 0.0 and 1.0
        raw_text: Original OCR output before normalization
    """
    text: str
    confidence: float
    raw_text: str
    
    def __post_init__(self):
        """Validate plate reading data after initialization."""
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Validate text is not empty
        if not self.text or not self.text.strip():
            raise ValueError("Plate text cannot be empty")


@dataclass
class ViolationInfo:
    """Represents violation information from the compliance database.
    
    Attributes:
        plate_number: License plate number
        category: Violation category (e.g., "expired_inspection", "stolen")
        details: Additional information about the violation
        date_added: Date when entry was added to database
    """
    plate_number: str
    category: str
    details: str
    date_added: str
    
    def __post_init__(self):
        """Validate violation info after initialization."""
        if not self.plate_number or not self.plate_number.strip():
            raise ValueError("Plate number cannot be empty")
        if not self.category or not self.category.strip():
            raise ValueError("Category cannot be empty")


@dataclass
class ViolationRecord:
    """Represents a complete violation record for reporting.
    
    Attributes:
        plate_number: License plate number
        violation_category: Type of violation
        frame_number: Frame where violation was detected
        timestamp: Time in video when detected
        video_source: Source video filename
        detection_confidence: Vehicle detection confidence
        ocr_confidence: OCR reading confidence
        bbox: Vehicle bounding box coordinates
    """
    plate_number: str
    violation_category: str
    frame_number: int
    timestamp: float
    video_source: str
    detection_confidence: float
    ocr_confidence: float
    bbox: Tuple[int, int, int, int]
    
    def __post_init__(self):
        """Validate violation record after initialization."""
        if not self.plate_number or not self.plate_number.strip():
            raise ValueError("Plate number cannot be empty")
        if not self.violation_category or not self.violation_category.strip():
            raise ValueError("Violation category cannot be empty")
        
        # Validate confidences
        if not 0.0 <= self.detection_confidence <= 1.0:
            raise ValueError(f"Detection confidence must be between 0.0 and 1.0, got {self.detection_confidence}")
        if not 0.0 <= self.ocr_confidence <= 1.0:
            raise ValueError(f"OCR confidence must be between 0.0 and 1.0, got {self.ocr_confidence}")
        
        # Validate frame number and timestamp
        if self.frame_number < 0:
            raise ValueError(f"Frame number must be non-negative, got {self.frame_number}")
        if self.timestamp < 0:
            raise ValueError(f"Timestamp must be non-negative, got {self.timestamp}")
        
        # Validate bounding box
        x1, y1, x2, y2 = self.bbox
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            raise ValueError(f"Bounding box coordinates must be non-negative, got {self.bbox}")
        if x2 <= x1:
            raise ValueError(f"x2 must be greater than x1, got x1={x1}, x2={x2}")
        if y2 <= y1:
            raise ValueError(f"y2 must be greater than y1, got y1={y1}, y2={y2}")


@dataclass
class VideoMetadata:
    """Represents metadata about a video file.
    
    Attributes:
        filename: Video filename
        duration: Video duration in seconds
        fps: Original frames per second
        resolution: Video resolution as (width, height)
        total_frames: Total number of frames in video
    """
    filename: str
    duration: float
    fps: float
    resolution: Tuple[int, int]
    total_frames: int
    
    def __post_init__(self):
        """Validate video metadata after initialization."""
        if not self.filename or not self.filename.strip():
            raise ValueError("Filename cannot be empty")
        if self.duration < 0:
            raise ValueError(f"Duration must be non-negative, got {self.duration}")
        if self.fps <= 0:
            raise ValueError(f"FPS must be positive, got {self.fps}")
        if self.total_frames < 0:
            raise ValueError(f"Total frames must be non-negative, got {self.total_frames}")
        
        width, height = self.resolution
        if width <= 0 or height <= 0:
            raise ValueError(f"Resolution dimensions must be positive, got {self.resolution}")


@dataclass
class PipelineConfig:
    """Configuration for the processing pipeline.
    
    Attributes:
        vehicle_confidence_threshold: Minimum confidence for vehicle detections
        plate_confidence_threshold: Minimum confidence for plate detections
        ocr_confidence_threshold: Minimum confidence for OCR readings
        frame_extraction_fps: Target FPS for frame extraction
        database_path: Path to compliance database CSV file
        output_dir: Directory for output files
        enable_analytics: Whether to generate analytics
        enable_anonymization: Whether to anonymize compliant vehicles
    """
    vehicle_confidence_threshold: float = 0.5
    plate_confidence_threshold: float = 0.6
    ocr_confidence_threshold: float = 0.7
    frame_extraction_fps: int = 5
    database_path: str = "data/watchlist.csv"
    output_dir: str = "outputs"
    enable_analytics: bool = True
    enable_anonymization: bool = False
    
    def __post_init__(self):
        """Validate pipeline configuration after initialization."""
        # Validate confidence thresholds
        if not 0.0 <= self.vehicle_confidence_threshold <= 1.0:
            raise ValueError(f"Vehicle confidence threshold must be between 0.0 and 1.0, got {self.vehicle_confidence_threshold}")
        if not 0.0 <= self.plate_confidence_threshold <= 1.0:
            raise ValueError(f"Plate confidence threshold must be between 0.0 and 1.0, got {self.plate_confidence_threshold}")
        if not 0.0 <= self.ocr_confidence_threshold <= 1.0:
            raise ValueError(f"OCR confidence threshold must be between 0.0 and 1.0, got {self.ocr_confidence_threshold}")
        
        # Validate FPS
        if self.frame_extraction_fps <= 0:
            raise ValueError(f"Frame extraction FPS must be positive, got {self.frame_extraction_fps}")
