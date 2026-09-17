"""OCR engine for reading license plate text.

This module provides the OCREngine class for extracting text from
license plate images using EasyOCR.
"""

import logging
import re
import numpy as np
from typing import Optional
import easyocr
from models import PlateReading


logger = logging.getLogger(__name__)


class OCREngine:
    """Extracts text from license plate images using OCR.
    
    This class uses EasyOCR to read text from license plate images,
    normalize the output, and filter by confidence threshold.
    
    Attributes:
        reader: EasyOCR Reader instance
        confidence_threshold: Minimum confidence for OCR results
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize OCREngine with EasyOCR.
        
        Args:
            confidence_threshold: Minimum confidence score for OCR results (0.0-1.0)
            
        Raises:
            ValueError: If confidence threshold is not between 0.0 and 1.0
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(f"Confidence threshold must be between 0.0 and 1.0, got {confidence_threshold}")
        
        self.confidence_threshold = confidence_threshold
        
        logger.info("Initializing EasyOCR reader...")
        try:
            # Initialize EasyOCR with English language
            # gpu=True will use GPU if available, falls back to CPU otherwise
            self.reader = easyocr.Reader(['en'], gpu=True, verbose=False)
            logger.info("EasyOCR reader initialized successfully")
            logger.info(f"Confidence threshold: {confidence_threshold}")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def read_plate(self, plate_image: np.ndarray) -> Optional[PlateReading]:
        """Extract text from a license plate image.
        
        Args:
            plate_image: Cropped license plate image as numpy array (BGR format)
            
        Returns:
            PlateReading object with text and confidence, or None if reading fails
            or confidence is below threshold
        """
        if plate_image is None or plate_image.size == 0:
            logger.warning("Empty plate image provided to OCR engine")
            return None
        
        try:
            # Run OCR
            results = self.reader.readtext(plate_image)
            
            if not results:
                logger.debug("No text detected in plate image")
                return None
            
            # Get the result with highest confidence
            # EasyOCR returns list of (bbox, text, confidence)
            best_result = max(results, key=lambda x: x[2])
            bbox, raw_text, confidence = best_result
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                logger.debug(f"OCR confidence {confidence:.3f} below threshold {self.confidence_threshold}")
                return None
            
            # Normalize the text
            normalized_text = self.normalize_plate(raw_text)
            
            # Validate normalized text is not empty
            if not normalized_text or not normalized_text.strip():
                logger.debug("Normalized text is empty")
                return None
            
            # Create PlateReading object
            plate_reading = PlateReading(
                text=normalized_text,
                confidence=confidence,
                raw_text=raw_text
            )
            
            logger.debug(f"OCR result: '{normalized_text}' (confidence: {confidence:.3f})")
            return plate_reading
            
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return None
    
    def normalize_plate(self, raw_text: str) -> str:
        """Normalize license plate text.
        
        Normalization steps:
        1. Convert to uppercase
        2. Remove all whitespace
        3. Remove special characters (keep only alphanumeric)
        4. Handle common OCR mistakes (O/0, I/1, etc.)
        
        Args:
            raw_text: Raw OCR output text
            
        Returns:
            Normalized plate text (uppercase, no spaces, alphanumeric only)
        """
        if not raw_text:
            return ""
        
        # Convert to uppercase
        text = raw_text.upper()
        
        # Remove all whitespace
        text = re.sub(r'\s+', '', text)
        
        # Remove special characters, keep only alphanumeric
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        # Handle common OCR mistakes
        # Note: This is context-dependent. For license plates:
        # - First characters are usually letters
        # - Last characters are usually numbers
        # For MVP, we'll keep it simple and not make assumptions
        
        return text
    
    def preprocess_plate_image(self, plate_image: np.ndarray) -> np.ndarray:
        """Preprocess plate image to improve OCR accuracy.
        
        This method applies image preprocessing techniques to enhance
        text visibility and improve OCR results.
        
        Args:
            plate_image: Input plate image
            
        Returns:
            Preprocessed plate image
        """
        import cv2
        
        # Convert to grayscale
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        
        # Apply adaptive thresholding to handle varying lighting
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        processed = cv2.fastNlMeansDenoising(processed)
        
        return processed


def main():
    """Test the OCREngine with a sample plate image."""
    import sys
    import cv2
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("\n=== Testing OCREngine ===\n")
        
        # Initialize OCR engine
        print("Initializing OCR engine (this may take a moment)...")
        ocr = OCREngine(confidence_threshold=0.7)
        print("✅ OCR engine initialized\n")
        
        # Test normalization function
        print("=== Testing Normalization ===")
        test_cases = [
            "ABC 123",
            "abc-123",
            "A B C 1 2 3",
            "  XYZ789  ",
            "O0O 1I1",
        ]
        
        for test_text in test_cases:
            normalized = ocr.normalize_plate(test_text)
            print(f"'{test_text}' → '{normalized}'")
        
        # Test with actual image if provided
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            print(f"\n=== Testing with image: {image_path} ===")
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not read image: {image_path}")
                return 1
            
            print(f"Image shape: {image.shape}")
            
            # Run OCR
            print("Running OCR...")
            result = ocr.read_plate(image)
            
            if result:
                print(f"\n✅ OCR Success!")
                print(f"   Raw text: '{result.raw_text}'")
                print(f"   Normalized: '{result.text}'")
                print(f"   Confidence: {result.confidence:.3f}")
            else:
                print("\n❌ No text detected or confidence too low")
        else:
            print("\n💡 Tip: Provide an image path to test OCR on actual plate image")
            print("   Example: python src/ocr_engine.py path/to/plate.jpg")
        
        print("\n✅ OCREngine test completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
