import customtkinter as ctk
from datetime import datetime, timedelta
from ...database.database import Database
from ...database.models import Session

class StatsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Stats content gets more space
        
        # Create filters frame
        self.create_filters_frame()
        
        # Create stats content
        self.create_stats_frame()
        
        # Initialize filters
        self.load_stakes_options()
        
        # Load initial stats
        self.update_stats()
        
    def create_filters_frame(self):
        filters_frame = ctk.CTkFrame(self)
        filters_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filters_frame.grid_columnconfigure((0,1,2), weight=1)
        
        # Date range filter
        date_frame = ctk.CTkFrame(filters_frame)
        date_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(date_frame, text="Date Range:").pack(side="left", padx=5)
        self.date_var = ctk.StringVar(value="All Time")
        date_options = ["Last Week", "Last Month", "Last 3 Months", "Last Year", "All Time"]
        date_dropdown = ctk.CTkOptionMenu(
            date_frame, 
            values=date_options,
            variable=self.date_var,
            command=self.update_stats
        )
        date_dropdown.pack(side="left", padx=5)
        
        # Stakes filter
        stakes_frame = ctk.CTkFrame(filters_frame)
        stakes_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(stakes_frame, text="Stakes:").pack(side="left", padx=5)
        self.stakes_listbox = ctk.CTkOptionMenu(
            stakes_frame,
            values=["Loading..."],
            command=self.update_stats
        )
        self.stakes_listbox.pack(side="left", padx=5)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            filters_frame,
            text="Refresh Stats",
            command=self.update_stats,
            fg_color="#287C37",  # Dark green
            hover_color="#1D5827"  # Darker green for hover
        )
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
    def create_stats_frame(self):
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.stats_frame.grid_columnconfigure((0,1), weight=1)
        
        # Create labels for stats (will be updated later)
        self.profit_per_hour = ctk.CTkLabel(
            self.stats_frame, 
            text="$/hour: -",
            font=("Arial", 16, "bold")
        )
        self.profit_per_hour.grid(row=0, column=0, padx=20, pady=20)
        
        self.profit_per_hand = ctk.CTkLabel(
            self.stats_frame, 
            text="$/hand: -",
            font=("Arial", 16, "bold")
        )
        self.profit_per_hand.grid(row=0, column=1, padx=20, pady=20)
        
        self.sessions_won = ctk.CTkLabel(
            self.stats_frame, 
            text="Sessions Won: -",
            font=("Arial", 16, "bold")
        )
        self.sessions_won.grid(row=1, column=0, padx=20, pady=20)
        
        self.win_percentage = ctk.CTkLabel(
            self.stats_frame, 
            text="Win Rate: -%",
            font=("Arial", 16, "bold")
        )
        self.win_percentage.grid(row=1, column=1, padx=20, pady=20)
        
    def load_stakes_options(self):
        db = Database()
        session = db.get_session()
        try:
            # Get unique stakes
            stakes = session.query(Session.stakes).distinct().all()
            stakes = [stake[0] for stake in stakes]
            stakes.insert(0, "All Stakes")  # Add "All Stakes" option
            
            # Update stakes listbox
            self.stakes_listbox.configure(values=stakes)
            self.stakes_listbox.set("All Stakes")
            
        finally:
            session.close()
            
    def get_date_filter(self):
        date_range = self.date_var.get()
        now = datetime.now()
        
        if date_range == "Last Week":
            return now - timedelta(days=7)
        elif date_range == "Last Month":
            return now - timedelta(days=30)
        elif date_range == "Last 3 Months":
            return now - timedelta(days=90)
        elif date_range == "Last Year":
            return now - timedelta(days=365)
        return None  # All Time
            
    def parse_duration(self, duration_str):
        """Convert duration string like '4m 33s' to hours"""
        minutes = 0
        seconds = 0
        
        # Split on 'm' and 's'
        parts = duration_str.split()
        for part in parts:
            if part.endswith('m'):
                minutes = float(part[:-1])
            elif part.endswith('s'):
                seconds = float(part[:-1])
        
        # Convert to hours
        return (minutes + seconds/60) / 60

    def update_stats(self, *args):
        db = Database()
        session = db.get_session()
        try:
            # Build query based on filters
            query = session.query(Session)
            
            # Apply date filter
            date_filter = self.get_date_filter()
            if date_filter:
                query = query.filter(Session.start_time >= date_filter)
                
            # Apply stakes filter
            stakes_filter = self.stakes_listbox.get()
            if stakes_filter != "All Stakes":
                query = query.filter(Session.stakes == stakes_filter)
                
            # Execute query
            sessions = query.all()
            
            if sessions:
                # Calculate stats
                total_profit = sum(s.result for s in sessions)
                # Parse duration strings and convert to hours
                total_hours = sum(self.parse_duration(s.duration) for s in sessions)
                total_hands = sum(s.hands_played for s in sessions)
                winning_sessions = sum(1 for s in sessions if s.result > 0)
                
                # Update labels
                self.profit_per_hour.configure(text=f"$/hour: ${total_profit/total_hours:.2f}" if total_hours else "$/hour: $0.00")
                self.profit_per_hand.configure(text=f"$/hand: ${total_profit/total_hands:.2f}" if total_hands else "$/hand: $0.00")
                self.sessions_won.configure(text=f"Sessions Won: {winning_sessions}/{len(sessions)}")
                self.win_percentage.configure(text=f"Win Rate: {(winning_sessions/len(sessions))*100:.1f}%")
            else:
                # Reset labels if no sessions found
                self.profit_per_hour.configure(text="$/hour: -")
                self.profit_per_hand.configure(text="$/hand: -")
                self.sessions_won.configure(text="Sessions Won: -")
                self.win_percentage.configure(text="Win Rate: -%")
                
        finally:
            session.close()