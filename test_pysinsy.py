"""
Quick test to verify PySinsy is installed and working.
"""

import pysinsy

print("Testing PySinsy installation...")
print(f"PySinsy version: {pysinsy.__version__ if hasattr(pysinsy, '__version__') else 'unknown'}")

# Try to initialize
try:
    sinsy = pysinsy.Sinsy()
    print("✓ Sinsy object created successfully")
    
    # Check for language dictionaries
    default_dic = pysinsy.get_default_dic_dir()
    print(f"✓ Default dictionary directory: {default_dic}")
    
    # Try to set English language
    result = sinsy.setLanguages("en", default_dic)
    if result:
        print("✓ English language set successfully")
    else:
        print("⚠ Warning: Could not set English language (might need dictionary files)")
    
    print("\n✓ PySinsy is installed and ready to use!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("PySinsy may need additional setup or dictionary files")

