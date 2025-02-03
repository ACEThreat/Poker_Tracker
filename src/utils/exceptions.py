class PokerTrackerError(Exception):
    """Base exception class for Poker Tracker"""
    pass

class ScrapingError(PokerTrackerError):
    """Raised when scraping fails"""
    pass

class DatabaseError(PokerTrackerError):
    """Raised when database operations fail"""
    pass 