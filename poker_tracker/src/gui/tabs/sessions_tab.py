import customtkinter as ctk
from ...database.database import Database
from ...database.models import Session
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.collections import LineCollection

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

class SessionsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.page_size = 50
        self.current_page = 0
        self.total_sessions = 0
        self.current_sort_column = 0
        self.sort_ascending = False
        
        # Configure main frame grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create filter frame
        self.create_filter_frame()
        
        # Create sessions table
        self.create_sessions_table()
        
        # Create pagination frame
        self.create_pagination_frame()
        
        # Initial data fetch
        self.fetch_sessions()

    def create_filter_frame(self):
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Stakes filter
        ctk.CTkLabel(filter_frame, text="Stakes:").grid(row=0, column=0, padx=5)
        self.stakes_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Stakes"],
            width=100
        )
        self.stakes_filter.grid(row=0, column=1, padx=5)
        
        # Game filter
        ctk.CTkLabel(filter_frame, text="Game:").grid(row=0, column=2, padx=5)
        self.game_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Games", "Hold'em", "Omaha"],
            width=100
        )
        self.game_filter.grid(row=0, column=3, padx=5)
        
        # Date range filter
        date_frame = ctk.CTkFrame(filter_frame)
        date_frame.grid(row=0, column=4, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(date_frame, text="Date:").pack(side="left", padx=5)
        self.date_var = ctk.StringVar(value="All Time")
        date_options = ["Custom", "Last Week", "Last Month", "Last 3 Months", "Last Year", "All Time"]
        self.date_filter = ctk.CTkOptionMenu(
            date_frame, 
            values=date_options,
            variable=self.date_var,
            command=self.on_date_range_change,
            width=100
        )
        self.date_filter.pack(side="left", padx=5)
        
        # Calendar date range (hidden by default)
        self.calendar_frame = ctk.CTkFrame(filter_frame)
        self.calendar_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=5, sticky="ew")
        self.calendar_frame.grid_remove()
        
        ctk.CTkLabel(self.calendar_frame, text="From:").pack(side="left", padx=2)
        self.start_date = DatePicker(self.calendar_frame)
        self.start_date.pack(side="left", padx=2)
        
        ctk.CTkLabel(self.calendar_frame, text="To:").pack(side="left", padx=2)
        self.end_date = DatePicker(self.calendar_frame)
        self.end_date.pack(side="left", padx=2)
        
        # Apply filters button
        self.filter_button = ctk.CTkButton(
            filter_frame,
            text="Apply Filters",
            command=self.apply_filters,
            width=100
        )
        self.filter_button.grid(row=0, column=6, padx=5)
        
        # Clear filters button
        self.clear_button = ctk.CTkButton(
            filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            width=100
        )
        self.clear_button.grid(row=0, column=7, padx=5)
        
        # Graph button
        self.graph_button = ctk.CTkButton(
            filter_frame,
            text="Show Graph",
            command=self.show_graph_window,
            width=100,
            fg_color="#2B5EA7",  # Blue color
            hover_color="#1E4175"
        )
        self.graph_button.grid(row=0, column=8, padx=5)
        
        # Load stakes options
        self.load_stakes_options()

    def load_stakes_options(self):
        db = Database()
        session = db.get_session()
        try:
            # Get unique stakes
            stakes = session.query(Session.stakes).distinct().all()
            stakes = ["All Stakes"] + [stake[0] for stake in stakes]
            
            # Update stakes dropdown
            self.stakes_filter.configure(values=stakes)
            self.stakes_filter.set("All Stakes")
            
        finally:
            session.close()

    def on_date_range_change(self, value):
        if value == "Custom":
            self.calendar_frame.grid()
        else:
            self.calendar_frame.grid_remove()
        self.apply_filters()

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

    def clear_filters(self):
        self.stakes_filter.set("All Stakes")
        self.game_filter.set("All Games")
        self.date_var.set("All Time")
        self.calendar_frame.grid_remove()
        self.apply_filters()

    def build_query(self, session):
        query = session.query(Session)
        
        # Apply stakes filter
        if self.stakes_filter.get() != "All Stakes":
            query = query.filter(Session.stakes == self.stakes_filter.get())
        
        # Apply game filter
        if self.game_filter.get() != "All Games":
            query = query.filter(Session.game_format == self.game_filter.get())
        
        # Apply date filter
        start_date, end_date = self.get_date_filter()
        if start_date and end_date:
            query = query.filter(Session.start_time >= start_date, Session.start_time <= end_date)
        
        # Apply sorting
        sort_col = Session.start_time
        if self.current_sort_column == 1:
            sort_col = Session.stakes
        elif self.current_sort_column == 2:
            sort_col = Session.game_format
        elif self.current_sort_column == 4:
            sort_col = Session.hands_played
        elif self.current_sort_column == 5:
            sort_col = Session.result
            
        if self.sort_ascending:
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))
            
        return query

    def fetch_sessions(self):
        db = Database()
        session = db.get_session()
        try:
            query = self.build_query(session)
            
            # Get total count
            self.total_sessions = query.count()
            
            # Get paginated results
            sessions = query.offset(self.current_page * self.page_size).limit(self.page_size).all()
            
            self.update_table(sessions)
            self.update_pagination_controls()
        finally:
            session.close()

    def update_pagination_controls(self):
        total_pages = (self.total_sessions + self.page_size - 1) // self.page_size
        self.page_label.configure(text=f"Page {self.current_page + 1} of {total_pages}")
        
        self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")

    def next_page(self):
        self.current_page += 1
        self.fetch_sessions()

    def prev_page(self):
        self.current_page -= 1
        self.fetch_sessions()

    def sort_table(self, column):
        if self.current_sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.current_sort_column = column
            self.sort_ascending = True
        self.fetch_sessions()

    def create_sessions_table(self):
        # Create scrollable container
        self.table_container = ctk.CTkScrollableFrame(
            self,
            width=800,  # Adjust width as needed
            height=400  # Adjust height as needed
        )
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure column weights for the container
        for i in range(8):
            self.table_container.grid_columnconfigure(i, weight=1)
        
        # Headers
        headers = ["Date", "Stakes", "Game", "Duration", "Hands", "Result", "BB/100", "$/Hour"]
        for i, header in enumerate(headers):
            header_button = ctk.CTkButton(
                self.table_container,
                text=header,
                font=("Arial", 14, "bold"),
                command=lambda col=i: self.sort_table(col),
                height=40
            )
            header_button.grid(row=0, column=i, padx=5, pady=(5, 10), sticky="ew")

    def update_table(self, sessions):
        """Update table with session data"""
        self.clear_table()
        
        for row_idx, s in enumerate(sessions, start=1):
            # Calculate stats
            duration_hours = self.parse_duration(s.duration)
            bb_size = float(s.stakes.split('/')[1].strip().split()[0])
            bb_per_100 = (s.result / bb_size * 100) / s.hands_played if s.hands_played > 0 else 0
            hourly_rate = s.result / duration_hours if duration_hours > 0 else 0
            
            cells = [
                s.start_time.strftime("%Y-%m-%d %H:%M"),
                s.stakes,
                s.game_format,
                s.duration,
                str(s.hands_played),
                f"${s.result:.2f}",
                f"{bb_per_100:.2f}",
                f"${hourly_rate:.2f}"
            ]
            
            for col, value in enumerate(cells):
                ctk.CTkLabel(
                    self.table_container,  # Changed from self.table_frame
                    text=str(value),
                    font=("Arial", 12),
                    anchor="center"
                ).grid(row=row_idx, column=col, padx=5, pady=4, sticky="ew")

    def clear_table(self):
        """Clear all rows except headers"""
        for widget in self.table_container.grid_slaves():  # Changed from self.table_frame
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
    
    def parse_duration(self, duration_str):
        """Convert duration string to hours"""
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

    def apply_filters(self):
        self.current_page = 0
        self.fetch_sessions()

    def create_pagination_frame(self):
        """Create pagination controls at the bottom of the table"""
        pagination_frame = ctk.CTkFrame(self)
        pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Previous page button
        self.prev_button = ctk.CTkButton(
            pagination_frame,
            text="Previous",
            command=self.prev_page,
            width=100,
            state="disabled"
        )
        self.prev_button.pack(side="left", padx=5)
        
        # Page label
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            width=100
        )
        self.page_label.pack(side="left", padx=5)
        
        # Next page button
        self.next_button = ctk.CTkButton(
            pagination_frame,
            text="Next",
            command=self.next_page,
            width=100,
            state="disabled"
        )
        self.next_button.pack(side="left", padx=5)

    def show_graph_window(self):
        # Create new window
        graph_window = ctk.CTkToplevel(self)
        graph_window.title("Session Results Graph")
        graph_window.geometry("800x600")
        
        # Create graph frame in new window
        graph_frame = ctk.CTkFrame(graph_window)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add control frame for axis selection
        control_frame = ctk.CTkFrame(graph_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Create frames for Y and X axis controls
        y_axis_frame = ctk.CTkFrame(control_frame)
        y_axis_frame.pack(side="left", padx=10)
        
        x_axis_frame = ctk.CTkFrame(control_frame)
        x_axis_frame.pack(side="left", padx=10)
        
        # Y-axis controls
        ctk.CTkLabel(y_axis_frame, text="Y-axis:").pack(side="left", padx=5)
        self.y_axis_var = ctk.StringVar(value="dollars")
        
        ctk.CTkRadioButton(
            y_axis_frame,
            text="Dollars ($)",
            variable=self.y_axis_var,
            value="dollars",
            command=lambda: self.update_graph(ax, canvas)
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            y_axis_frame,
            text="Big Blinds",
            variable=self.y_axis_var,
            value="bb",
            command=lambda: self.update_graph(ax, canvas)
        ).pack(side="left", padx=5)
        
        # X-axis controls
        ctk.CTkLabel(x_axis_frame, text="X-axis:").pack(side="left", padx=5)
        self.x_axis_var = ctk.StringVar(value="sessions")
        
        ctk.CTkRadioButton(
            x_axis_frame,
            text="Sessions",
            variable=self.x_axis_var,
            value="sessions",
            command=lambda: self.update_graph(ax, canvas)
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            x_axis_frame,
            text="Hours",
            variable=self.x_axis_var,
            value="hours",
            command=lambda: self.update_graph(ax, canvas)
        ).pack(side="left", padx=5)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initial graph update
        self.update_graph(ax, canvas)

    def update_graph(self, ax, canvas):
        """Update the graph with session data"""
        db = Database()
        session = db.get_session()
        try:
            query = self.build_query(session)
            sessions = query.order_by(Session.start_time).all()
            
            if sessions:
                ax.clear()
                
                # Calculate cumulative results and hours
                results = []
                hours = []
                cumulative_hours = 0
                
                for s in sessions:
                    if self.y_axis_var.get() == "dollars":
                        results.append(s.result)
                    else:  # bb
                        bb_size = float(s.stakes.split('/')[1].strip().split()[0])
                        results.append(s.result / bb_size)
                    
                    # Calculate hours for this session
                    duration_str = s.duration
                    duration_hours = self.parse_duration(duration_str)
                    cumulative_hours += duration_hours
                    hours.append(cumulative_hours)
                
                cumulative = np.cumsum(results)
                
                # Choose x-axis values based on selection
                if self.x_axis_var.get() == "sessions":
                    x_values = range(len(sessions))
                    ax.set_xlabel('Sessions')
                else:  # hours
                    x_values = hours
                    ax.set_xlabel('Hours')
                
                # Create the line plot
                line = ax.plot(x_values, cumulative, label='Cumulative Profit')[0]
                
                # Color the line segments based on y-values
                points = np.array([x_values, cumulative]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                
                # Create a LineCollection with different colors
                lc = LineCollection(segments, colors=['#287C37' if y >= 0 else '#FF3B30' 
                                                    for y in cumulative[1:]])
                ax.add_collection(lc)
                line.remove()  # Remove the original line
                
                # Fill between line and x-axis with colors
                ax.fill_between(x_values, cumulative, 0, 
                              where=(cumulative >= 0), color='#287C37', alpha=0.1)
                ax.fill_between(x_values, cumulative, 0, 
                              where=(cumulative < 0), color='#FF3B30', alpha=0.1)
                
                ax.grid(True)
                
                if self.y_axis_var.get() == "dollars":
                    ax.set_ylabel('Profit ($)')
                else:
                    ax.set_ylabel('Profit (BB)')
                
                ax.set_title('Poker Session Results')
                
            else:
                ax.clear()
                ax.grid(True)
                ax.set_xlabel('Sessions')
                ax.set_ylabel('Profit')
                ax.set_title('Poker Session Results (No Data)')
                
            canvas.draw()
            
        finally:
            session.close() 