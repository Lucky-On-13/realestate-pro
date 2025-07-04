import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton
from config import Config
from property_management import PropertyManagementWindow
from user_management import UserManagementWindow
from transaction_management import TransactionManagementWindow
from analytics_dashboard import AnalyticsDashboard

class AdminDashboard:
    def __init__(self, parent, db_manager, admin_user):
        self.parent = parent
        self.db_manager = db_manager
        self.admin_user = admin_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("RealEstate Pro - Admin Dashboard")
        self.window.geometry("1400x900")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_dashboard_data()
    
    def create_widgets(self):
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the admin dashboard header"""
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            header_content,
            text="Admin Dashboard",
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side="left")
        
        # Admin info
        admin_info = tk.Label(
            header_content,
            text=f"Welcome, {self.admin_user['first_name']} {self.admin_user['last_name']}",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        admin_info.pack(side="right", padx=(0, 20))
        
        # Logout button
        logout_btn = ModernButton(
            header_content,
            text="Logout",
            command=self.logout,
            style="outline"
        )
        logout_btn.pack(side="right")
    
    def create_main_content(self):
        """Create the main dashboard content"""
        main_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Overview tab
        self.create_overview_tab()
        
        # Quick actions tab
        self.create_quick_actions_tab()
        
        # System info tab
        self.create_system_info_tab()
    
    def create_overview_tab(self):
        """Create overview tab with statistics"""
        overview_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(overview_frame, text="Overview")
        
        # Statistics cards container
        stats_container = tk.Frame(overview_frame, bg=Config.BACKGROUND_COLOR)
        stats_container.pack(fill="x", pady=(0, 20))
        
        # Statistics cards
        self.stats_cards = {}
        stats_data = [
            ("Total Properties", "properties_count", Config.PRIMARY_COLOR),
            ("Active Users", "users_count", Config.SECONDARY_COLOR),
            ("Total Transactions", "transactions_count", Config.ACCENT_COLOR),
            ("Revenue This Month", "monthly_revenue", Config.SUCCESS_COLOR)
        ]
        
        for i, (title, key, color) in enumerate(stats_data):
            card = self.create_stat_card(stats_container, title, "Loading...", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.stats_cards[key] = card
        
        # Configure grid weights
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)
        
        # Recent activity section
        activity_frame = tk.Frame(overview_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        activity_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        activity_header = tk.Label(
            activity_frame,
            text="Recent Activity",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        activity_header.pack(pady=10)
        
        # Activity list
        self.activity_listbox = tk.Listbox(
            activity_frame,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY,
            selectbackground=Config.PRIMARY_COLOR,
            height=10
        )
        self.activity_listbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        
        # Header with color
        header_frame = tk.Frame(card_frame, bg=color, height=5)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Content
        content_frame = tk.Frame(card_frame, bg=Config.CARD_COLOR)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_SECONDARY
        )
        title_label.pack()
        
        value_label = tk.Label(
            content_frame,
            text=value,
            font=(Config.FONT_FAMILY, 20, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        value_label.pack(pady=(5, 0))
        
        # Store reference to value label for updates
        card_frame.value_label = value_label
        
        return card_frame
    
    def create_quick_actions_tab(self):
        """Create quick actions tab"""
        actions_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(actions_frame, text="Quick Actions")
        
        # Actions grid
        actions_container = tk.Frame(actions_frame, bg=Config.BACKGROUND_COLOR)
        actions_container.pack(expand=True)
        
        # Management buttons
        management_buttons = [
            ("Manage Properties", self.open_property_management, Config.PRIMARY_COLOR),
            ("Manage Users", self.open_user_management, Config.SECONDARY_COLOR),
            ("View Transactions", self.open_transaction_management, Config.ACCENT_COLOR),
            ("Analytics Dashboard", self.open_analytics, Config.SUCCESS_COLOR)
        ]
        
        for i, (text, command, color) in enumerate(management_buttons):
            row = i // 2
            col = i % 2
            
            btn = ModernButton(
                actions_container,
                text=text,
                command=command,
                style="primary",
                bg=color,
                width=20,
                height=3
            )
            btn.grid(row=row, column=col, padx=20, pady=20, sticky="ew")
        
        # Configure grid
        actions_container.columnconfigure(0, weight=1)
        actions_container.columnconfigure(1, weight=1)
    
    def create_system_info_tab(self):
        """Create system information tab"""
        info_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(info_frame, text="System Info")
        
        # System info content
        info_content = tk.Frame(info_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        info_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_header = tk.Label(
            info_content,
            text="System Information",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        info_header.pack(pady=20)
        
        # System details
        system_info = [
            ("Application Name", Config.APP_NAME),
            ("Version", Config.VERSION),
            ("Database Host", Config.DB_HOST),
            ("Database Name", Config.DB_NAME),
            ("Admin User", f"{self.admin_user['first_name']} {self.admin_user['last_name']}"),
            ("Admin Email", self.admin_user['email'])
        ]
        
        for label, value in system_info:
            info_row = tk.Frame(info_content, bg=Config.CARD_COLOR)
            info_row.pack(fill="x", padx=40, pady=5)
            
            tk.Label(
                info_row,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                width=20,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                info_row,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left", padx=(10, 0))
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Frame(self.window, bg=Config.BORDER_COLOR, height=25)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            text="Admin Dashboard Ready",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BORDER_COLOR,
            fg=Config.TEXT_SECONDARY,
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=2)
    
    def load_dashboard_data(self):
        """Load dashboard statistics and recent activity"""
        try:
            # Get statistics
            stats = self.db_manager.get_admin_statistics()
            
            # Update stat cards
            self.stats_cards['properties_count'].value_label.configure(text=str(stats['total_properties']))
            self.stats_cards['users_count'].value_label.configure(text=str(stats['total_users']))
            self.stats_cards['transactions_count'].value_label.configure(text=str(stats['total_transactions']))
            self.stats_cards['monthly_revenue'].value_label.configure(text=f"${stats['monthly_revenue']:,.0f}")
            
            # Load recent activity
            activities = self.db_manager.get_recent_activities(limit=20)
            self.activity_listbox.delete(0, tk.END)
            
            for activity in activities:
                self.activity_listbox.insert(tk.END, activity)
            
            self.update_status("Dashboard data loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard data: {str(e)}")
            self.update_status("Error loading dashboard data")
    
    def open_property_management(self):
        """Open property management window"""
        PropertyManagementWindow(self.window, self.db_manager, self.admin_user)
    
    def open_user_management(self):
        """Open user management window"""
        UserManagementWindow(self.window, self.db_manager, self.admin_user)
    
    def open_transaction_management(self):
        """Open transaction management window"""
        TransactionManagementWindow(self.window, self.db_manager, self.admin_user)
    
    def open_analytics(self):
        """Open analytics dashboard"""
        AnalyticsDashboard(self.window, self.db_manager, self.admin_user)
    
    def logout(self):
        """Handle admin logout"""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            self.window.destroy()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.window.after(5000, lambda: self.status_label.configure(text="Admin Dashboard Ready"))