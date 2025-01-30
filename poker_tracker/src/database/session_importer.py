from .database import Database
from .models import Session
from datetime import datetime

class SessionImporter:
    def __init__(self):
        self.db = Database()

    def import_sessions(self, sessions):
        """Import sessions into database with de-duplication"""
        session = self.db.get_session()
        duplicates = 0
        imported = 0
        
        try:
            for session_data in sessions:
                # Check for existing session with matching criteria
                existing_session = session.query(Session).filter(
                    Session.start_time == session_data['start_time'],
                    Session.duration == session_data['duration'],
                    Session.hands_played == session_data['hands_played'],
                    Session.result == session_data['result']
                ).first()
                
                if existing_session:
                    duplicates += 1
                    continue
                
                # Create new Session object
                new_session = Session(
                    start_time=session_data['start_time'],
                    duration=session_data['duration'],
                    game_format=session_data['game_format'],
                    stakes=session_data['stakes'],
                    hands_played=session_data['hands_played'],
                    result=session_data['result'],
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