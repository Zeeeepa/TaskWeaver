#!/usr/bin/env python3
"""
Enhanced run script for TaskWeaver UI with Codegen integration
"""

import os
import sys
import logging

from standalone_taskweaver.ui.main_enhanced import main

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-run-enhanced")

if __name__ == "__main__":
    main()

