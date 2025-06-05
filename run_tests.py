import subprocess
import sys
import os

def run_tests():
    """Run the tests using Python 3.11"""
    # Get the path to Python 3.11
    python_path = r"C:\Users\matzu\AppData\Local\Programs\Python\Python311\python.exe"
    
    if not os.path.exists(python_path):
        print("❌ Python 3.11 not found at:", python_path)
        print("Please make sure Python 3.11 is installed")
        sys.exit(1)
    
    print("🚀 Running tests with Python 3.11...")
    
    # Run pytest with Python 3.11
    result = subprocess.run([
        python_path,
        "-m",
        "pytest",
        "tests/test_supabase.py",
        "-v"
    ])
    
    # Exit with the same code as pytest
    sys.exit(result.returncode)

if __name__ == "__main__":
    run_tests() 