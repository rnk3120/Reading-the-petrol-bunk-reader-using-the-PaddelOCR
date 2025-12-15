#!/usr/bin/env python3
"""
Ollama Vision Validator
Validates OCR results using local LLaVA model
"""

import base64
import json
import cv2
import numpy as np
from io import BytesIO

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[WARN] requests library not found. Install with: pip install requests")


class OllamaValidator:
    def __init__(self, model="llava", base_url="http://localhost:11434"):
        """
        Initialize the Ollama validator
        
        Args:
            model: Name of the vision model (default: llava)
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required. Run: pip install requests")
        
        # Test connection
        try:
            response = requests.get(base_url, timeout=2)
            print(f"[INFO] Ollama validator connected to {base_url}")
        except Exception as e:
            print(f"[WARN] Could not connect to Ollama: {e}")
            print("[WARN] Make sure Ollama is running. Try: ollama serve")
    
    def frame_to_base64(self, frame):
        """Convert OpenCV frame to base64 string"""
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        # Convert to base64
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return img_base64
    
    def validate_meter_reading(self, frame, roi_name="ROI_3", expected_format="decimal"):
        """
        Ask Ollama to read a specific meter value from the frame
        
        Args:
            frame: OpenCV image (BGR)
            roi_name: Which ROI we're validating (for context)
            expected_format: "decimal" or "integer"
        
        Returns:
            dict with 'value' and 'confidence'
        """
        try:
            # Convert frame to base64
            img_b64 = self.frame_to_base64(frame)
            
            # Craft the prompt
            if expected_format == "decimal":
                prompt = """Look at this meter display. Find the main numeric reading (usually the largest number in the center).
This is a decimal number that may have a decimal point.
Return ONLY the number, nothing else. If you see '34567', it might actually be '345.67'.
Format: XXX.XX

Number:"""
            else:
                prompt = f"""Look at this display and find the value for {roi_name}.
Return ONLY the number you see, nothing else.

Number:"""
            
            # Make API request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30  # Increased timeout for slower systems
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_text = result.get('response', '').strip()
                
                # Extract just the number from the response
                import re
                # Look for decimal numbers first
                match = re.search(r'\d+\.\d+', raw_text)
                if not match:
                    # Look for integers
                    match = re.search(r'\d+', raw_text)
                
                if match:
                    value = match.group(0)
                    return {
                        'value': value,
                        'confidence': 0.9,  # Ollama doesn't provide confidence, assume high
                        'raw_response': raw_text
                    }
                else:
                    return {
                        'value': None,
                        'confidence': 0.0,
                        'raw_response': raw_text
                    }
            else:
                print(f"[ERROR] Ollama API error: {response.status_code}")
                return {'value': None, 'confidence': 0.0, 'raw_response': ''}
                
        except Exception as e:
            print(f"[ERROR] Ollama validation failed: {e}")
            return {'value': None, 'confidence': 0.0, 'raw_response': str(e)}
    
    def batch_validate(self, frame, roi_dict):
        """
        Validate multiple ROIs at once
        
        Args:
            frame: OpenCV image
            roi_dict: Dictionary like {'ROI_1': '123', 'ROI_2': '456', ...}
        
        Returns:
            Dictionary with validated values
        """
        # For now, just validate the main ROI (ROI_3)
        # You can extend this to validate all ROIs
        result = self.validate_meter_reading(frame, roi_name="ROI_3")
        return {
            'ROI_3': result['value'],
            'confidence': result['confidence'],
            'raw_response': result.get('raw_response', '')
        }


def test_validator():
    """Test function"""
    print("Testing Ollama Validator...")
    
    validator = OllamaValidator()
    
    # Create a test image with text
    test_img = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "345.67", (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5)
    
    result = validator.validate_meter_reading(test_img)
    print(f"Result: {result}")


if __name__ == "__main__":
    test_validator()
