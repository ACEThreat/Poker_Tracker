import customtkinter as ctk
from datetime import datetime, timedelta
from ...database.database import Database
from ...database.models import Session
from ...utils.stats_calculator import StatsCalculator
import logging

logger = logging.getLogger(__name__)

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
        # Add this line at the start of __init__ to filter out StatsCalculator logs
        logging.getLogger('poker_tracker.src.utils.stats_calculator').setLevel(logging.WARNING)
        
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
        
        self.total_hands = ctk.CTkLabel(
            session_frame,
            text="Total Hands: -",
            font=("Arial", 16)
        )
        self.total_hands.grid(row=1, column=1, padx=20, pady=10)
        
        self.hands_per_hour = ctk.CTkLabel(
            session_frame,
            text="Hands/Hour: -",
            font=("Arial", 16)
        )
        self.hands_per_hour.grid(row=2, column=0, padx=20, pady=10)
        
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
        
        # Add upswing/downswing labels
        self.best_streak = ctk.CTkLabel(
            extremes_frame, 
            text="Best Streak: -",
            font=("Arial", 16)
        )
        self.best_streak.grid(row=1, column=0, padx=20, pady=10)
        
        self.worst_streak = ctk.CTkLabel(
            extremes_frame, 
            text="Worst Streak: -",
            font=("Arial", 16)
        )
        self.worst_streak.grid(row=1, column=1, padx=20, pady=10)
        
        # Variance frame
        variance_frame = ctk.CTkFrame(self.stats_frame)
        variance_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        variance_frame.grid_columnconfigure((0,1), weight=1)
        
        self.bb_per_100 = ctk.CTkLabel(
            variance_frame,
            text="BB/100: -",
            font=("Arial", 16)
        )
        self.bb_per_100.grid(row=0, column=0, padx=20, pady=10)
        
        self.std_dev = ctk.CTkLabel(
            variance_frame,
            text="Std Dev (BB): -",
            font=("Arial", 16)
        )
        self.std_dev.grid(row=0, column=1, padx=20, pady=10)
        
        # Add to variance frame
        self.bankroll_rec = ctk.CTkLabel(
            variance_frame,
            text="Recommended Bankroll: - buyins",
            font=("Arial", 16)
        )
        self.bankroll_rec.grid(row=1, column=0, columnspan=2, padx=20, pady=10)
        
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

    def calculate_streaks(self, sessions):
        """Calculate best and worst streaks using cumulative results, including BB data"""
        if not sessions:
            return (0, 0, 0, 0), (0, 0, 0, 0)  # (profit, BB, sessions, hands) for best and worst
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
        
        # For tracking streak details
        best_streak = {'profit': 0, 'bb': 0, 'sessions': 0, 'hands': 0, 'start_idx': 0}
        worst_streak = {'profit': 0, 'bb': 0, 'sessions': 0, 'hands': 0, 'start_idx': 0}
        
        for i, session in enumerate(sorted_sessions):
            # Check for new best/worst streak from any previous point to here
            for j in range(i + 1):
                profit_in_range = 0
                bb_in_range = 0
                hands_in_range = 0
                
                # Calculate total profit and BB for this range
                for s in sorted_sessions[j:i+1]:
                    profit_in_range += s.result if s.result else 0
                    hands_in_range += s.hands_played if s.hands_played else 0
                    
                    try:
                        stakes_parts = s.stakes.split('/')
                        if len(stakes_parts) >= 2:
                            bb_str = ''.join(c for c in stakes_parts[1] if c.isdigit() or c == '.')
                            bb_size = float(bb_str) if bb_str else 1
                            bb_result = s.result / bb_size if s.result else 0
                            bb_in_range += bb_result
                    except (ValueError, IndexError, AttributeError) as e:
                        print(f"Warning: Could not process stakes {s.stakes}: {e}")
                        continue
                
                if profit_in_range > best_streak['profit']:
                    best_streak.update({
                        'profit': profit_in_range,
                        'bb': bb_in_range,
                        'sessions': i - j + 1,
                        'hands': hands_in_range
                    })
                if profit_in_range < worst_streak['profit']:
                    worst_streak.update({
                        'profit': profit_in_range,
                        'bb': bb_in_range,
                        'sessions': i - j + 1,
                        'hands': hands_in_range
                    })
        
        return (
            (best_streak['profit'], best_streak['bb'], best_streak['sessions'], best_streak['hands']),
            (worst_streak['profit'], worst_streak['bb'], worst_streak['sessions'], worst_streak['hands'])
        )

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
                total_hands = sum(s.hands_played for s in sessions)
                
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
                self.total_hands.configure(text=f"Total Hands: {total_hands:,}")
                
                # Calculate hands per hour
                hands_per_hour = int(total_hands / total_hours) if total_hours else 0
                self.hands_per_hour.configure(text=f"Hands/Hour: {hands_per_hour:,}")
                
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
                
                # Calculate and display streaks
                best_streak, worst_streak = self.calculate_streaks(sessions)
                
                # Format streak information
                best_amount, best_color = format_currency(best_streak[0])
                self.best_streak.configure(
                    text=f"Best Streak: {best_amount} ({best_streak[1]:,.1f} BB)\n({best_streak[2]} sessions, {best_streak[3]:,} hands)",
                    text_color=best_color
                )
                
                worst_amount, worst_color = format_currency(worst_streak[0])
                self.worst_streak.configure(
                    text=f"Worst Streak: {worst_amount} ({worst_streak[1]:,.1f} BB)\n({worst_streak[2]} sessions, {worst_streak[3]:,} hands)",
                    text_color=worst_color
                )
                
                # Get all results in BB for Hold'em sessions only
                holdem_sessions = [s for s in sessions if s.game_format == "Hold'em"]
                if holdem_sessions:
                    total_bb_won = 0
                    total_hands = 0
                    
                    for s in holdem_sessions:
                        try:
                            # Extract BB size from stakes (e.g., "1 SC / 2 SC" -> 2)
                            bb_size = float(s.stakes.split('/')[1].strip().split()[0])
                            # Convert result to BB (if result is $100 and BB is $2, that's 50 BB)
                            bb_result = s.result / bb_size
                            # Add to running totals
                            total_bb_won += bb_result
                            total_hands += s.hands_played
                        except (IndexError, ValueError) as e:
                            logger.warning(f"Could not process stakes {s.stakes}: {e}")
                            continue
                    
                    if total_hands > 0:
                        # Calculate BB/100: (total BB won / total hands) * 100
                        bb_per_100 = (total_bb_won / total_hands) * 100
                        
                        # For standard deviation, use session-level results
                        bb_results = []
                        for s in holdem_sessions:
                            try:
                                bb_size = float(s.stakes.split('/')[1].strip().split()[0])
                                bb_result = s.result / bb_size
                                # Convert to BB/100 for each session
                                bb_per_100_session = (bb_result / s.hands_played) * 100
                                bb_results.append(bb_per_100_session)
                            except (IndexError, ValueError, ZeroDivisionError):
                                continue
                        
                        # Calculate variance stats on BB/100 results
                        mean, variance, std_dev = StatsCalculator.calculate_variance_stats(bb_results, len(bb_results))
                        
                        # Update labels
                        self.bb_per_100.configure(
                            text=f"BB/100: {bb_per_100:.2f}",
                            text_color=color_amount(bb_per_100)
                        )
                        self.std_dev.configure(
                            text=f"Std Dev (BB/100): {std_dev:.2f}"
                        )
                        
                        # Pass win rate (BB/100) first, then std dev
                        recommended_buyins, warning_msg = StatsCalculator.recommend_bankroll(std_dev, bb_per_100)
                        
                        if recommended_buyins is None:
                            self.bankroll_rec.configure(
                                text=warning_msg,
                                text_color="#FF3B30"  # Red color for warning
                            )
                        else:
                            # Divide recommended buyins by 2 to get correct value
                            recommended_buyins = recommended_buyins / 2
                            self.bankroll_rec.configure(
                                text=f"Recommended Bankroll: {recommended_buyins:.0f} buyins (${recommended_buyins * bb_size * 100:,.2f})",
                                text_color="white"  # Reset to default color
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
                self.bb_per_100.configure(text="BB/100: -")
                self.std_dev.configure(text="Std Dev (BB): -")
                self.total_hands.configure(text="Total Hands: -")
                self.hands_per_hour.configure(text="Hands/Hour: -")
                self.best_streak.configure(text="Best Streak: -")
                self.worst_streak.configure(text="Worst Streak: -")
                self.bankroll_rec.configure(text="Recommended Bankroll: - buyins")
                
        finally:
            session.close()