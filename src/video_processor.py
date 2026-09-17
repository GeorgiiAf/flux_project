"""Video processing component for extracting frames from video files.

This module provides the VideoProcessor class for reading video files,
extracting frames at specified intervals, and retrieving video metadata.
"""

import cv2
import logging
from typing import Iterator, Optional
from pathlib import Path
from models import Frame, VideoMetadata


logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video files and extracts frames with metadata.
    
    This class handles video file reading, frame extraction at configurable
    frame rates, and metadata extraction. It supports common video formats
    including MP4, AVI, and MOV.
    
    Attributes:
        video_path: Path to the video file
        fps: Target frame rate for extraction (frames per second)
        video_name: Filename without path
    """
    
    def __init__(self, video_path: str, fps: int = 5):
        """Initialize VideoProcessor with video path and target FPS.
        
        Args:
            video_path: Path to the video file to process
            fps: Target frame rate for extraction (default: 5 fps)
            
        Raises:
            FileNotFoundError: If video file does not exist
            ValueError: If fps is not positive
        """
        self.video_path = Path(video_path)
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if fps <= 0:
            raise ValueError(f"FPS must be positive, got {fps}")
        
        self.fps = fps
        self.video_name = self.video_path.name
        logger.info(f"Initialized VideoProcessor for {self.video_name} with target FPS={fps}")
    
    def extract_frames(self) -> Iterator[Frame]:
        """Extract frames from video at the specified frame rate.
        
        Yields frames as Frame objects with image data and metadata.
        Handles corrupted frames gracefully by logging errors and continuing.
        
        Yields:
            Frame: Frame objects containing image data and metadata
            
        Raises:
            RuntimeError: If video cannot be opened
        """
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video file: {self.video_path}")
        
        try:
            # Get video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            if original_fps == 0:
                logger.warning(f"Could not determine FPS for {self.video_name}, using default 30")
                original_fps = 30.0
            
            # Calculate frame interval for target FPS
            frame_interval = max(1, int(original_fps / self.fps))
            
            frame_count = 0
            extracted_count = 0
            
            logger.info(f"Starting frame extraction from {self.video_name}")
            logger.info(f"Original FPS: {original_fps:.2f}, Target FPS: {self.fps}, Frame interval: {frame_interval}")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    # End of video or read error
                    break
                
                # Extract frame at specified interval
                if frame_count % frame_interval == 0:
                    # Check if frame is valid
                    if frame is None or frame.size == 0:
                        logger.warning(f"Skipping corrupted frame at position {frame_count}")
                        frame_count += 1
                        continue
                    
                    # Calculate timestamp
                    timestamp = frame_count / original_fps
                    
                    try:
                        # Create Frame object
                        frame_obj = Frame(
                            image=frame,
                            frame_number=extracted_count,
                            timestamp=timestamp,
                            video_source=self.video_name
                        )
                        
                        yield frame_obj
                        extracted_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error creating Frame object at position {frame_count}: {e}")
                        # Continue processing other frames
                
                frame_count += 1
            
            logger.info(f"Extracted {extracted_count} frames from {frame_count} total frames in {self.video_name}")
            
        finally:
            cap.release()
            logger.debug(f"Released video capture for {self.video_name}")
    
    def get_video_info(self) -> VideoMetadata:
        """Extract metadata from the video file.
        
        Returns:
            VideoMetadata: Object containing video duration, resolution, fps, etc.
            
        Raises:
            RuntimeError: If video cannot be opened or metadata cannot be read
        """
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video file: {self.video_path}")
        
        try:
            # Extract video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Handle cases where FPS is not available
            if fps == 0:
                logger.warning(f"FPS not available for {self.video_name}, using default 30")
                fps = 30.0
            
            # Calculate duration
            if total_frames > 0 and fps > 0:
                duration = total_frames / fps
            else:
                logger.warning(f"Could not calculate duration for {self.video_name}")
                duration = 0.0
            
            metadata = VideoMetadata(
                filename=self.video_name,
                duration=duration,
                fps=fps,
                resolution=(width, height),
                total_frames=total_frames
            )
            
            logger.info(f"Video metadata for {self.video_name}: "
                       f"{width}x{height}, {fps:.2f} fps, {duration:.2f}s, {total_frames} frames")
            
            return metadata
            
        finally:
            cap.release()


def main():
    """Test the VideoProcessor with sample videos."""
    import sys
    
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
        # Create processor
        processor = VideoProcessor(video_path, fps=5)
        
        # Get video info
        print("\n=== Video Metadata ===")
        metadata = processor.get_video_info()
        print(f"Filename: {metadata.filename}")
        print(f"Duration: {metadata.duration:.2f} seconds")
        print(f"FPS: {metadata.fps:.2f}")
        print(f"Resolution: {metadata.resolution[0]}x{metadata.resolution[1]}")
        print(f"Total Frames: {metadata.total_frames}")
        
        # Extract and count frames
        print("\n=== Extracting Frames ===")
        frame_count = 0
        for frame in processor.extract_frames():
            frame_count += 1
            if frame_count <= 3:
                print(f"Frame {frame.frame_number}: timestamp={frame.timestamp:.2f}s, "
                      f"shape={frame.image.shape}, source={frame.video_source}")
        
        print(f"\nTotal frames extracted: {frame_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
