import sys
import os
import pytest

# Redirect stdout to file
sys.stdout = open("test_run.log", "w", encoding="utf-8")
sys.stderr = sys.stdout

# Add src to path just in case
sys.path.append(os.path.abspath(os.curdir))

print("Running tests...")
retcode = pytest.main(["-v", "tests/test_integration.py"])
print(f"Tests finished with exit code: {retcode}")
