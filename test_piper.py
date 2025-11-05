#!/usr/bin/env python3
"""
Test script for piper-tts
"""

import subprocess
import sys

# Test basic functionality
print("Testing piper-tts...")

# Use piper directly via command line (easier than Python API)
try:
    # Test if piper is installed
    result = subprocess.run(
        ["piper", "--help"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("✗ Piper command not found")
        print("Install with: pip install piper-tts")
        sys.exit(1)
    
    print("✓ Piper installed")
    
    # Generate test audio using command line
    test_text = "Hello, this is a test."
    output_file = "test_piper_output.wav"
    
    print("Generating test audio...")
    result = subprocess.run(
        ["piper", "--model", "en_US-lessac-medium", "--output_file", output_file],
        input=test_text,
        text=True,
        capture_output=True
    )
    
    if result.returncode == 0:
        print(f"✓ Generated test audio: {output_file}")
        print("  Play it to test quality!")
    else:
        print(f"✗ Error generating audio:")
        print(result.stderr)
    
except Exception as e:
    print(f"✗ Error: {e}")

