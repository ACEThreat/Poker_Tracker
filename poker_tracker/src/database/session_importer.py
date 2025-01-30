from .database import Database
from .models import Session
from datetime import datetime, timedelta

class SessionImporter:
    def __init__(self):
        self.db = Database()

    def import_sessions(self, sessions):
        """Import sessions into database with de-duplication"""
        session = self.db.get_session()
        duplicates = 0
        imported = 0
        
        try:
            # Sort sessions by start time
            sorted_sessions = sorted(sessions, key=lambda x: x['start_time'])
            current_total_hours = 0
            current_end = None
            
            for session_data in sorted_sessions:
                # Check for existing session
                existing_session = session.query(Session).filter(
                    Session.start_time == session_data['start_time'],
                    Session.duration == session_data['duration'],
                    Session.hands_played == session_data['hands_played'],
                    Session.result == session_data['result']
                ).first()
                
                if existing_session:
                    duplicates += 1
                    continue
                
                # Calculate session duration in hours
                duration_hours = self.parse_duration(session_data['duration'])
                start = session_data['start_time']
                end = start + timedelta(hours=duration_hours)
                
                # Calculate non-overlapping hours
                if current_end is None:
                    current_total_hours += duration_hours
                else:
                    if start > current_end:
                        # No overlap
                        current_total_hours += duration_hours
                    else:
                        # Handle overlap
                        if end > current_end:
                            current_total_hours += (end - current_end).total_seconds() / 3600
                
                current_end = max(end, current_end) if current_end else end
                
                # Create new Session object with total_hours
                new_session = Session(
                    start_time=session_data['start_time'],
                    duration=session_data['duration'],
                    game_format=session_data['game_format'],
                    stakes=session_data['stakes'],
                    hands_played=session_data['hands_played'],
                    result=session_data['result'],
                    total_hours=current_total_hours,
                    created_at=datetime.utcnow()
                )
                session.add(new_session)
                imported += 1
            
            # Commit the transaction
            session.commit()
            message = f"Imported {imported} sessions"
            if duplicates > 0:
                message += f" (skipped {duplicates} duplicates)"
            return True, message
            
        except Exception as e:
            session.rollback()
            return False, f"Error importing sessions: {str(e)}"
        finally:
            session.close()

    def parse_duration(self, duration_str):
        """Convert duration string like '2h 45m 41s' to hours"""
        hours = 0
        minutes = 0
        seconds = 0
        
        parts = duration_str.split()
        for part in parts:
            if part.endswith('h'):
                hours = float(part[:-1])
            elif part.endswith('m'):
                minutes = float(part[:-1])
            elif part.endswith('s'):
                seconds = float(part[:-1])
        
        return hours + (minutes / 60) + (seconds / 3600) 