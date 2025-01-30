import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from ...database.database import Database
from ...database.models import Session
from tkinter import Toplevel

class SessionsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure main frame grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Give table more weight
        
        # Create sessions table first (will take most space)
        self.create_sessions_table()
        
        # Create button frame at the bottom
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Add Show Graph button with blue color
        self.graph_button = ctk.CTkButton(
            button_frame,
            text="Show Graph",
            command=self.show_graph_window,
            width=120,
            fg_color="#2B5EA7",  # Darker blue
            hover_color="#1E4175"  # Even darker blue for hover
        )
        self.graph_button.pack(side="left", padx=5, pady=5)
        
        # Add Refresh button with green color
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh Data",
            command=self.fetch_sessions,
            width=120,
            fg_color="#287C37",  # Dark green
            hover_color="#1D5827"  # Darker green for hover
        )
        self.refresh_button.pack(side="left", padx=5, pady=5)
        
        # Initialize session data list
        self.session_data_list = []
        
        # Add sort state initialization
        self.current_sort_column = 0  # Stakes column
        self.sort_ascending = True
        
        # Initial data fetch
        self.fetch_sessions()
    
    def create_sessions_table(self):
        # Main table frame with increased padding
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure column weights for the main frame
        for i in range(5):
            self.table_frame.grid_columnconfigure(i, weight=1)
        
        # Headers with increased size and padding
        headers = ["Stake", "Game", "Won", "Hands", "BB/100"]
        for i, header in enumerate(headers):
            header_button = ctk.CTkButton(
                self.table_frame,
                text=header,
                font=("Arial", 14, "bold"),  # Increased font size
                command=lambda col=i: self.sort_table(col),
                height=40  # Increased height
            )
            header_button.grid(row=0, column=i, padx=5, pady=(5, 10), sticky="ew")

    def show_graph_window(self):
        # Create new window
        graph_window = Toplevel(self)
        graph_window.title("Session Results Graph")
        graph_window.geometry("800x600")
        
        # Create graph frame in new window
        graph_frame = ctk.CTkFrame(graph_window)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Update graph with data - pass the session_data_list
        self.update_graph(ax, canvas, self.session_data_list)
        
    def update_graph(self, ax, canvas, sessions_data=None):
        """Update the graph with new session data"""
        ax.clear()
        if sessions_data:
            sessions = range(len(sessions_data))
            cumulative_profit = np.cumsum([s.get('profit', 0) for s in sessions_data])
            ax.plot(sessions, cumulative_profit, '-b', label='Cumulative Profit')
            ax.grid(True)
            ax.set_xlabel('Sessions')
            ax.set_ylabel('Profit ($)')
            ax.set_title('Poker Session Results')
        else:
            # Display empty graph with grid
            ax.grid(True)
            ax.set_xlabel('Sessions')
            ax.set_ylabel('Profit ($)')
            ax.set_title('Poker Session Results (No Data)')
        canvas.draw()

    def fetch_sessions(self):
        """Fetch sessions from database and update display"""
        db = Database()
        session = db.get_session()
        try:
            # Get all sessions ordered by start time
            sessions = session.query(Session).order_by(Session.start_time.desc()).all()
            
            if not sessions:
                return
            
            # Store sessions data for graph updates
            self.session_data_list = [{'profit': float(s.result)} for s in sessions]
            
            # Update table with aggregated data
            self.update_table(sessions)
            
            print(f"Fetched {len(sessions)} sessions from database")
            print(f"Total profit: ${sum(s.result for s in sessions):.2f}")
            
        except Exception as e:
            print(f"Error fetching sessions: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

    def sort_table(self, column):
        """Sort table data based on clicked column"""
        if self.current_sort_column == column:
            # If clicking the same column, reverse the sort order
            self.sort_ascending = not self.sort_ascending
        else:
            # New column, default to ascending
            self.sort_ascending = True
            self.current_sort_column = column
        
        # Convert grouped_data to list for sorting
        data_list = [(stakes, game, data) for (stakes, game), data in self.grouped_data.items()]
        
        # Define sort key functions for each column
        sort_keys = {
            0: lambda x: x[0],  # Stakes
            1: lambda x: x[1],  # Game
            2: lambda x: x[2]['total_profit'],  # Won
            3: lambda x: x[2]['hands'],  # Hands
            4: lambda x: (x[2]['total_profit'] / x[2]['bb_size'] * 100) / x[2]['hands'] 
               if x[2]['hands'] > 0 else 0  # BB/100
        }
        
        # Sort the data
        data_list.sort(
            key=sort_keys[column],
            reverse=not self.sort_ascending
        )
        
        # Clear and rebuild the table with sorted data
        self.clear_table()
        
        # Rebuild table with sorted data
        for row_idx, (stakes, game, data) in enumerate(data_list, start=1):
            profit_in_bb = data['total_profit'] / data['bb_size']
            bb_per_100 = (profit_in_bb * 100) / data['hands'] if data['hands'] > 0 else 0
            
            cells = [
                stakes,
                game,
                f"${data['total_profit']:.2f}",
                str(data['hands']),
                f"{bb_per_100:.2f}"
            ]
            
            for col, value in enumerate(cells):
                ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=("Arial", 12),  # Increased font size
                    anchor="center"  # Center align text
                ).grid(row=row_idx, column=col, padx=5, pady=4, sticky="ew")

    def clear_table(self):
        """Clear all rows except headers"""
        for widget in self.table_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

    def update_table(self, sessions):
        """Update the sessions table with aggregated data"""
        self.clear_table()
        
        # Group sessions by stakes and game format
        self.grouped_data = {}
        for s in sessions:
            key = (s.stakes, s.game_format)
            if key not in self.grouped_data:
                self.grouped_data[key] = {
                    'hands': 0,
                    'total_profit': 0,
                    'bb_size': float(s.stakes.split('/')[1].strip().split()[0])
                }
            
            data = self.grouped_data[key]
            data['hands'] += s.hands_played
            data['total_profit'] += s.result
        
        # Initial sort by stakes ascending
        self.current_sort_column = 0  # Stakes column
        self.sort_ascending = True
        self.sort_table(0)

    def add_session_row(self, data, row):
        """Add a row of session data to the table"""
        row_frame = ctk.CTkFrame(self.sessions_table_frame)
        row_frame.grid(row=row, column=0, sticky="ew", padx=2, pady=2)
        row_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        for col, value in enumerate(data):
            ctk.CTkLabel(row_frame, text=str(value)).grid(
                row=0, column=col, padx=5, pady=2, sticky="ew"
            ) 