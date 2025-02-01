def parse_duration(duration_str):
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