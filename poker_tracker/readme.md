# Poker Tracker

A comprehensive poker session tracking and analysis tool designed for unfriendly poker sites.

## Features

- Track poker session results and statistics
- Analyze performance with detailed graphs and metrics
- Import sessions automatically from supported poker sites
- Calculate variance and recommended bankroll
- Cross-platform support (Windows, macOS, Linux)
- Advanced bankroll management tools
- Real-time statistics and performance tracking
- Manual bankroll adjustments
- Automated session importing from Clubs Poker
- Detailed performance analytics (BB/100, hourly rate, etc.)
- Customizable graphs and data visualization
- Backup and restore functionality

## Requirements

- Python 3.8 or higher
- Google Chrome (for automated session importing)
- Operating System: Windows, macOS, or Linux

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/poker_tracker.git
cd poker_tracker
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Super Beginner's Guide

### Windows Installation (No Git Required)

1. Download the program:
   - Go to the releases page
   - Download the latest `poker_tracker.zip` file
   - Extract the zip file to a folder (e.g., `C:\PokerTracker`)

2. Install Python:
   - Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
   - Click "Install Now" with all default options

3. Install the program:
   - Open Command Prompt (search for "cmd" in Start menu)
   - Navigate to the folder where you extracted the files:
     ```
     cd C:\PokerTracker
     ```
   - Create a virtual environment:
     ```
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - Install required packages:
     ```
     pip install -r requirements.txt
     ```

4. Start the program:
   - Double-click the `run.bat` file in the PokerTracker folder
   OR
   - In Command Prompt:
     ```
     python main.py
     ```

### macOS Installation (No Git Required)

1. Download the program:
   - Go to the releases page
   - Download the latest `poker_tracker.zip` file
   - Extract the zip file to a folder (e.g., `~/PokerTracker`)

2. Install Python:
   - Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
   - Open the downloaded `.pkg` file and follow installation instructions
   - During installation, the default options are fine

3. Install the program:
   - Open Terminal (search for "Terminal" in Spotlight)
   - Navigate to the folder where you extracted the files:
     ```
     cd ~/PokerTracker
     ```
   - Create a virtual environment:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Install required packages:
     ```
     pip install -r requirements.txt
     ```

4. Start the program:
   - Double-click the `run.command` file in the PokerTracker folder
   OR
   - In Terminal:
     ```
     python main.py
     ```

### Troubleshooting

1. "Python not found" error:
   - Make sure Python is installed
   - Try using `python3` instead of `python` on macOS
   - Restart your computer after installing Python

2. Chrome profile issues:
   - Make sure Google Chrome is installed
   - Log into your poker site in Chrome before using auto-import
   - Follow the Chrome profile setup instructions in the app

3. Import not working:
   - Ensure you're logged into your poker site in Chrome
   - Close Chrome completely before importing
   - Follow the on-screen instructions carefully

For more detailed instructions or help, see the full documentation above.

## Getting Started

1. Start the application:
```