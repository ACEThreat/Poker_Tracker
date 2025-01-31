import customtkinter as ctk
from ...database.database import Database
from ...database.models import Session
from datetime import datetime
from sqlalchemy import desc, asc

class SessionsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.page_size = 50
        self.current_page = 0
        self.total_sessions = 0
        self.current_sort_column = 0
        self.sort_ascending = False
        self.filters = {
            'date': '',
            'stakes': '',
            'game': '',
            'result': ''
        }
        
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
        self.stakes_filter = ctk.CTkEntry(filter_frame, width=100)
        self.stakes_filter.grid(row=0, column=1, padx=5)
        
        # Game filter
        ctk.CTkLabel(filter_frame, text="Game:").grid(row=0, column=2, padx=5)
        self.game_filter = ctk.CTkEntry(filter_frame, width=100)
        self.game_filter.grid(row=0, column=3, padx=5)
        
        # Result filter
        ctk.CTkLabel(filter_frame, text="Result:").grid(row=0, column=4, padx=5)
        self.result_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Winning", "Losing"],
            width=100
        )
        self.result_filter.grid(row=0, column=5, padx=5)
        
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

    def create_pagination_frame(self):
        pagination_frame = ctk.CTkFrame(self)
        pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.prev_button = ctk.CTkButton(
            pagination_frame,
            text="Previous",
            command=self.prev_page,
            width=100
        )
        self.prev_button.pack(side="left", padx=5)
        
        self.page_label = ctk.CTkLabel(pagination_frame, text="")
        self.page_label.pack(side="left", padx=5)
        
        self.next_button = ctk.CTkButton(
            pagination_frame,
            text="Next",
            command=self.next_page,
            width=100
        )
        self.next_button.pack(side="left", padx=5)

    def apply_filters(self):
        self.current_page = 0
        self.filters = {
            'stakes': self.stakes_filter.get(),
            'game': self.game_filter.get(),
            'result': self.result_filter.get()
        }
        self.fetch_sessions()

    def clear_filters(self):
        self.stakes_filter.delete(0, 'end')
        self.game_filter.delete(0, 'end')
        self.result_filter.set("All")
        self.apply_filters()

    def build_query(self, session):
        query = session.query(Session)
        
        if self.filters['stakes']:
            query = query.filter(Session.stakes.like(f"%{self.filters['stakes']}%"))
        
        if self.filters['game']:
            query = query.filter(Session.game_format.like(f"%{self.filters['game']}%"))
        
        if self.filters['result'] == "Winning":
            query = query.filter(Session.result > 0)
        elif self.filters['result'] == "Losing":
            query = query.filter(Session.result < 0)
        
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