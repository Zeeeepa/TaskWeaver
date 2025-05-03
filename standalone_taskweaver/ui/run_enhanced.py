#!/usr/bin/env python3
"""
Run script for the enhanced TaskWeaver UI
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from standalone_taskweaver.ui.main_enhanced import main

if __name__ == "__main__":
    main()

