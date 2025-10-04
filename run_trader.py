#!/usr/bin/env python
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTrading bot stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
