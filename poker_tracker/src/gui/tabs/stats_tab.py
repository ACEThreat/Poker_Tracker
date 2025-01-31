import customtkinter as ctk
from datetime import datetime, timedelta
from ...database.database import Database
from ...database.models import Session

class DatePicker(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        current_date = datetime.now()
        
        # Create frame for year, month, day
        self.year_var = ctk.StringVar(value=str(current_date.year))
        self.month_var = ctk.StringVar(value=str(current_date.month))
        self.day_var = ctk.StringVar(value=str(current_date.day))
        
        # Year dropdown
        years = [str(year) for year in range(current_date.year-5, current_date.year+1)]
        year_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.year_var,
            values=years,
            width=70
        )
        year_dropdown.pack(side="left", padx=2)
        
        # Month dropdown
        months = [str(m) for m in range(1, 13)]
        month_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.month_var,
            values=months,
            width=50
        )
        month_dropdown.pack(side="left", padx=2)
        
        # Day dropdown
        days = [str(d) for d in range(1, 32)]
        day_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.day_var,
            values=days,
            width=50
        )
        day_dropdown.pack(side="left", padx=2)
    
    def get_date(self):
        """Return datetime object for selected date"""
        return datetime(
            int(self.year_var.get()),
            int(self.month_var.get()),
            int(self.day_var.get())
        )

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
        filters_frame.grid_columnconfigure((0,1,2,3), weight=1)  # Added column for calendar
        
        # Date range filter
        date_frame = ctk.CTkFrame(filters_frame)
        date_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(date_frame, text="Date Range:").pack(side="left", padx=5)
        self.date_var = ctk.StringVar(value="All Time")
        date_options = ["Custom", "Last Week", "Last Month", "Last 3 Months", "Last Year", "All Time"]
        date_dropdown = ctk.CTkOptionMenu(
            date_frame, 
            values=date_options,
            variable=self.date_var,
            command=self.on_date_range_change
        )
        date_dropdown.pack(side="left", padx=5)
        
        # Calendar date range
        self.calendar_frame = ctk.CTkFrame(filters_frame)
        self.calendar_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.calendar_frame.grid_remove()  # Hidden by default
        
        ctk.CTkLabel(self.calendar_frame, text="From:").pack(side="left", padx=2)
        self.start_date = DatePicker(self.calendar_frame)
        self.start_date.pack(side="left", padx=2)
        
        ctk.CTkLabel(self.calendar_frame, text="To:").pack(side="left", padx=2)
        self.end_date = DatePicker(self.calendar_frame)
        self.end_date.pack(side="left", padx=2)
        
        # Move stakes filter to next column
        stakes_frame = ctk.CTkFrame(filters_frame)
        stakes_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
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
        refresh_btn.grid(row=0, column=3, padx=5, pady=5)
        
    def create_stats_frame(self):
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.stats_frame.grid_columnconfigure((0,1), weight=1)
        
        # Profit metrics frame
        profit_frame = ctk.CTkFrame(self.stats_frame)
        profit_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        profit_frame.grid_columnconfigure((0,1), weight=1)
        
        self.total_profit = ctk.CTkLabel(
            profit_frame, 
            text="Total Won: -",
            font=("Arial", 18, "bold")
        )
        self.total_profit.grid(row=0, column=0, padx=20, pady=10)
        
        self.profit_per_hour = ctk.CTkLabel(
            profit_frame, 
            text="$/hour: -",
            font=("Arial", 18, "bold")
        )
        self.profit_per_hour.grid(row=0, column=1, padx=20, pady=10)
        
        self.profit_per_hand = ctk.CTkLabel(
            profit_frame, 
            text="$/hand: -",
            font=("Arial", 18, "bold")
        )
        self.profit_per_hand.grid(row=1, column=0, padx=20, pady=10)
        
        # Session metrics frame
        session_frame = ctk.CTkFrame(self.stats_frame)
        session_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        session_frame.grid_columnconfigure((0,1), weight=1)
        
        self.sessions_won = ctk.CTkLabel(
            session_frame, 
            text="Sessions Won: -",
            font=("Arial", 16)
        )
        self.sessions_won.grid(row=0, column=0, padx=20, pady=10)
        
        self.win_percentage = ctk.CTkLabel(
            session_frame, 
            text="Win Rate: -%",
            font=("Arial", 16)
        )
        self.win_percentage.grid(row=0, column=1, padx=20, pady=10)
        
        self.total_time = ctk.CTkLabel(
            session_frame, 
            text="Total Time: -",
            font=("Arial", 16)
        )
        self.total_time.grid(row=1, column=0, padx=20, pady=10)
        
        # Best/Worst session frame
        extremes_frame = ctk.CTkFrame(self.stats_frame)
        extremes_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        extremes_frame.grid_columnconfigure((0,1), weight=1)
        
        self.biggest_win = ctk.CTkLabel(
            extremes_frame, 
            text="Biggest Win: -",
            font=("Arial", 16)
        )
        self.biggest_win.grid(row=0, column=0, padx=20, pady=10)
        
        self.biggest_loss = ctk.CTkLabel(
            extremes_frame, 
            text="Biggest Loss: -",
            font=("Arial", 16)
        )
        self.biggest_loss.grid(row=0, column=1, padx=20, pady=10)
        
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
            
    def on_date_range_change(self, value):
        if value == "Custom":
            self.calendar_frame.grid()
        else:
            self.calendar_frame.grid_remove()
        self.update_stats()

    def get_date_filter(self):
        date_range = self.date_var.get()
        now = datetime.now()
        
        if date_range == "Custom":
            start_date = datetime.combine(self.start_date.get_date(), datetime.min.time())
            end_date = datetime.combine(self.end_date.get_date(), datetime.max.time())
            return start_date, end_date
        elif date_range == "Last Week":
            return now - timedelta(days=7), now
        elif date_range == "Last Month":
            return now - timedelta(days=30), now
        elif date_range == "Last 3 Months":
            return now - timedelta(days=90), now
        elif date_range == "Last Year":
            return now - timedelta(days=365), now
        return None, None  # All Time
            
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

    def format_duration(self, hours):
        """Convert hours to a readable format"""
        total_minutes = int(hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"

    def update_stats(self, *args):
        db = Database()
        session = db.get_session()
        try:
            query = session.query(Session)
            
            # Apply date filter
            start_date, end_date = self.get_date_filter()
            if start_date and end_date:
                query = query.filter(Session.start_time >= start_date, Session.start_time <= end_date)
                
            # Apply stakes filter
            stakes_filter = self.stakes_listbox.get()
            if stakes_filter != "All Stakes":
                query = query.filter(Session.stakes == stakes_filter)
                
            # Execute query
            sessions = query.all()
            
            if sessions:
                # Calculate stats
                total_profit = sum(s.result for s in sessions)
                
                # Find biggest win and loss sessions
                biggest_win_session = max(sessions, key=lambda s: s.result)
                biggest_loss_session = min(sessions, key=lambda s: s.result)
                
                # Sort sessions by start time and handle overlaps
                sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
                total_hours = 0
                current_end = None
                
                for s in sorted_sessions:
                    start = s.start_time
                    duration_hours = self.parse_duration(s.duration)
                    end = start + timedelta(hours=duration_hours)
                    
                    if current_end is None:
                        total_hours += duration_hours
                    else:
                        if start > current_end:
                            # No overlap, add full duration
                            total_hours += duration_hours
                        else:
                            # Overlap exists, only add non-overlapping time
                            if end > current_end:
                                total_hours += (end - current_end).total_seconds() / 3600
                    
                    current_end = max(end, current_end) if current_end else end
                
                total_hands = sum(s.hands_played for s in sessions)
                winning_sessions = sum(1 for s in sessions if s.result > 0)
                
                # Helper function for color coding
                def color_amount(amount):
                    return "#287C37" if amount > 0 else "#FF3B30"
                
                # Format currency with color
                def format_currency(amount):
                    color = color_amount(amount)
                    return f"${abs(amount):,.2f}", color
                
                # Update labels
                amount, color = format_currency(total_profit)
                self.total_profit.configure(text=f"Total Won: {amount}", text_color=color)
                
                hourly_rate = total_profit/total_hours if total_hours else 0
                amount, color = format_currency(hourly_rate)
                self.profit_per_hour.configure(text=f"$/hour: {amount}", text_color=color)
                
                per_hand = total_profit/total_hands if total_hands else 0
                amount, color = format_currency(per_hand)
                self.profit_per_hand.configure(text=f"$/hand: {amount}", text_color=color)
                
                self.total_time.configure(text=f"Total Time: {self.format_duration(total_hours)}")
                self.sessions_won.configure(text=f"Sessions Won: {winning_sessions}/{len(sessions)}")
                self.win_percentage.configure(text=f"Win Rate: {(winning_sessions/len(sessions))*100:.1f}%")
                
                # Update biggest win/loss
                win_amount, win_color = format_currency(biggest_win_session.result)
                self.biggest_win.configure(
                    text=f"Biggest Win: {win_amount}\n{biggest_win_session.stakes} ({biggest_win_session.start_time.strftime('%Y-%m-%d')})",
                    text_color=win_color
                )
                
                loss_amount, loss_color = format_currency(biggest_loss_session.result)
                self.biggest_loss.configure(
                    text=f"Biggest Loss: {loss_amount}\n{biggest_loss_session.stakes} ({biggest_loss_session.start_time.strftime('%Y-%m-%d')})",
                    text_color=loss_color
                )
            else:
                # Reset labels if no sessions found
                self.total_profit.configure(text="Total Won: -")
                self.profit_per_hour.configure(text="$/hour: -")
                self.profit_per_hand.configure(text="$/hand: -")
                self.total_time.configure(text="Total Time: -")
                self.sessions_won.configure(text="Sessions Won: -")
                self.win_percentage.configure(text="Win Rate: -%")
                self.biggest_win.configure(text="Biggest Win: -")
                self.biggest_loss.configure(text="Biggest Loss: -")
                
        finally:
            session.close()