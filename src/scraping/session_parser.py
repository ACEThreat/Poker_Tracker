import re
from datetime import datetime
import os
from ..database.database import Database

class SessionParser:
    def __init__(self):
        app_dir = Database.get_app_directory()
        self.export_dir = os.path.join(app_dir, "DB_Import_Files")
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def parse_file(self, input_file):
        """Parse the scraped content file and extract session data"""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all table entries using the format from the scraped page
        table_entries = re.finditer(
            r"(Jan \d{1,2}, \d{1,2}:\d{2} [APM]{2})\n"  # Date and time
            r"((?:\d+h )?\d+m \d+s)\n"  # Duration
            r"(Hold'em|Omaha)\n"  # Game format
            r"([\d.]+ SC / [\d.]+ SC)\n"  # Stakes
            r"(\d+)\n"  # Hands played
            r"([+-][\d.]+ SC)",  # Result
            content
        )

        parsed_sessions = []
        for match in table_entries:
            start_time_str = match.group(1)
            duration = match.group(2)
            game_format = match.group(3)
            stakes = match.group(4)
            hands_played = int(match.group(5))
            result = float(match.group(6).replace(" SC", ""))

            # Parse start time
            start_time = datetime.strptime(start_time_str, "%b %d, %I:%M %p")
            start_time = start_time.replace(year=datetime.now().year)

            session = {
                'start_time': start_time,
                'duration': duration,
                'game_format': game_format,
                'stakes': stakes,
                'hands_played': hands_played,
                'result': result
            }
            parsed_sessions.append(session)

        # Save parsed sessions to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.export_dir, f'parsed_sessions_{timestamp}.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for session in parsed_sessions:
                f.write(f"Start time ({session['start_time'].strftime('%b %d, %I:%M %p')}) "
                       f"Duration ({session['duration']}) "
                       f"Format ({session['game_format']}) "
                       f"Stake ({session['stakes']}) "
                       f"HandsPlayed ({session['hands_played']}) "
                       f"Result (${session['result']:.2f})\n")

        return output_file

    def get_sessions(self, parsed_file):
        """Extract session data from parsed file"""
        sessions = []
        with open(parsed_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():  # Skip empty lines
                    continue
                    
                # Extract data using regex
                match = re.match(
                    r"Start time \((.*?)\) "
                    r"Duration \((.*?)\) "
                    r"Format \((.*?)\) "
                    r"Stake \((.*?)\) "
                    r"HandsPlayed \((\d+)\) "
                    r"Result \(\$([-\d.]+)\)",
                    line
                )
                
                if match:
                    start_time = datetime.strptime(match.group(1), "%b %d, %I:%M %p")
                    start_time = start_time.replace(year=datetime.now().year)
                    
                    session = {
                        'start_time': start_time,
                        'duration': match.group(2),
                        'game_format': match.group(3),
                        'stakes': match.group(4),
                        'hands_played': int(match.group(5)),
                        'result': float(match.group(6))
                    }
                    sessions.append(session)
        
        return sessions

    def parse_content(self, content):
        """Parse content string and return list of session dictionaries"""
        pattern = r"Start time \((.*?)\) Duration \((.*?)\) Format \((.*?)\) Stake \((.*?)\) HandsPlayed \((\d+)\) Result \(\$(.*?)\)"
        sessions = []
        
        for match in re.finditer(pattern, content):
            start_time_str, duration, game_format, stakes, hands_played, result = match.groups()
            
            start_time = datetime.strptime(start_time_str, "%b %d, %I:%M %p")
            start_time = start_time.replace(year=datetime.now().year)
            
            session = {
                'start_time': start_time,
                'duration': duration,
                'game_format': game_format,
                'stakes': stakes,
                'hands_played': int(hands_played),
                'result': float(result)
            }
            sessions.append(session)
            
        return sessions 