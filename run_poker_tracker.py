#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the poker_tracker directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from poker_tracker.src.gui.main_window import main

os.environ['NSSupportsAutomaticGraphicsSwitching'] = 'True'

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error starting Poker Tracker: {e}")
        sys.exit(1) 