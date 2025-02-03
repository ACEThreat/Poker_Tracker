#!/usr/bin/env python3
import sys
import os
from pathlib import Path

from src.gui.main_window import MainWindow

os.environ['NSSupportsAutomaticGraphicsSwitching'] = 'True'

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Poker Tracker: {e}")
        sys.exit(1) 