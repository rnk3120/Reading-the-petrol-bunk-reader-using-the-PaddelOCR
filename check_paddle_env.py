#!/usr/bin/env python3
"""
Quick installation verification and fix script for PaddleOCR setup
"""

import sys
import subprocess

def check_module(module_name, import_name=None):
    """Check if a module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        print(f"✗ {module_name} is NOT installed")
        return False

def main():
    print("=" * 60)
    print("PaddleOCR Environment Check")
    print("=" * 60)
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print()
    
    # Check required modules
    modules = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("shapely", "shapely"),
        ("scikit-learn", "sklearn"),
        ("PaddlePaddle", "paddle"),
        ("PaddleOCR", "paddleocr"),
        ("Pillow", "PIL"),
    ]
    
    missing = []
    for module_name, import_name in modules:
        if not check_module(module_name, import_name):
            missing.append(module_name)
    
    print()
    print("=" * 60)
    
    if missing:
        print("Missing modules:")
        for m in missing:
            print(f"  - {m}")
        print()
        print("To install missing modules, run:")
        print()
        
        if "PaddlePaddle" in missing:
            print("# For GPU (CUDA 11.2):")
            print("pip install paddlepaddle-gpu==2.5.1")
            print()
            print("# OR for CPU:")
            print("pip install paddlepaddle==2.5.1")
            print()
        
        if "PaddleOCR" in missing:
            print("pip install paddleocr")
            print()
        
        other_missing = [m for m in missing if m not in ["PaddlePaddle", "PaddleOCR"]]
        if other_missing:
            print(f"pip install {' '.join(other_missing)}")
            print()
    else:
        print("✓ All required modules are installed!")
        print()
        
        # Test PaddlePaddle
        try:
            import paddle
            print(f"PaddlePaddle version: {paddle.__version__}")
            print(f"Device: {paddle.device.get_device()}")
            
            # Test if GPU is available
            if paddle.device.is_compiled_with_cuda():
                print("✓ CUDA support is available")
                print(f"GPU count: {paddle.device.cuda.device_count()}")
            else:
                print("⚠ Running on CPU (CUDA not available)")
        except Exception as e:
            print(f"Error testing PaddlePaddle: {e}")
        
        print()
        print("You can now run your OCR script!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
