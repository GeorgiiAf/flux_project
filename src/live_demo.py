"""Live demo script that shows processing with visual feedback.

This script processes a video and displays the detections in real-time.
"""

import cv2
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from models import PipelineConfig
from video_processor import VideoProcessor
from vehicle_detector import VehicleDetector

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    """Run live demo with visual feedback."""
    
    # Get video path
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "data/videos/Clip1_morning.mp4"
    
    print("\n" + "="*70)
    print("LIVE DEMO - Vehicle Detection Visualization")
    print("="*70)
    print(f"\nProcessing: {video_path}")
    print("\nControls:")
    print("  - Press 'q' to quit")
    print("  - Press 'p' to pause/resume")
    print("  - Press 's' to save current frame")
    print("\nStarting in 3 seconds...")
    print("="*70 + "\n")
    
    # Initialize components
    print("Loading AI models...")
    vehicle_detector = VehicleDetector(confidence_threshold=0.5)
    video_processor = VideoProcessor(video_path, fps=5)
    
    print("✓ Models loaded\n")
    print("Processing video... (press 'q' to quit)\n")
    
    # Get video info
    metadata = video_processor.get_video_info()
    
    # Create window
    cv2.namedWindow('Vehicle Detection - Live Demo', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vehicle Detection - Live Demo', 1280, 720)
    
    paused = False
    frame_count = 0
    detection_count = 0
    
    try:
        for frame in video_processor.extract_frames():
            if not paused:
                # Detect vehicles
                detections = vehicle_detector.detect(
                    frame.image,
                    frame_number=frame.frame_number,
                    timestamp=frame.timestamp
                )
                
                # Draw detections
                display_frame = frame.image.copy()
                
                for detection in detections:
                    x1, y1, x2, y2 = detection.bbox
                    
                    # Choose color based on class
                    if detection.class_name == 'person':
                        color = (255, 0, 0)  # Blue for pedestrians
                    elif detection.class_name == 'bicycle':
                        color = (0, 255, 255)  # Yellow for cyclists
                    else:
                        color = (0, 255, 0)  # Green for vehicles
                    
                    # Draw bounding box
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label = f"{detection.class_name} {detection.confidence:.2f}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    
                    # Label background
                    cv2.rectangle(display_frame, 
                                (x1, y1 - label_size[1] - 10),
                                (x1 + label_size[0], y1),
                                color, -1)
                    
                    # Label text
                    cv2.putText(display_frame, label, (x1, y1 - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                # Add info overlay
                info_text = [
                    f"Frame: {frame.frame_number}",
                    f"Time: {frame.timestamp:.2f}s",
                    f"Detections: {len(detections)}",
                    f"Total: {detection_count}"
                ]
                
                y_offset = 30
                for text in info_text:
                    cv2.putText(display_frame, text, (10, y_offset),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30
                
                # Show frame
                cv2.imshow('Vehicle Detection - Live Demo', display_frame)
                
                frame_count += 1
                detection_count += len(detections)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n\nStopping...")
                break
            elif key == ord('p'):
                paused = not paused
                print(f"\n{'Paused' if paused else 'Resumed'}")
            elif key == ord('s'):
                save_path = f"outputs/frame_{frame.frame_number}.jpg"
                cv2.imwrite(save_path, display_frame)
                print(f"\n✓ Saved frame to {save_path}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cv2.destroyAllWindows()
        
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)
        print(f"Frames processed: {frame_count}")
        print(f"Total detections: {detection_count}")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
