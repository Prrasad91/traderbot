#!/usr/bin/env python
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTrading system stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
