import tkinter as tk
from tkinter import ttk, messagebox
import os
from database import DatabaseManager
from auth import AuthWindow
from admin_auth import AdminAuthWindow
from admin_dashboard import AdminDashboard
from property_details import PropertyDetailsWindow
from ui_components import ModernButton, PropertyCard, SearchFilter
from config import Config

class RealEstateApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(Config.APP_NAME)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.root.configure(bg=Config.BACKGROUND_COLOR)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Current user
        self.current_user = None
        
        # UI State
        self.current_listing_type = "sale"  # or "rent"
        self.current_filters = {}
        
        self.create_widgets()
        self.load_properties()
    
    def create_widgets(self):
        # Create main container
        self.main_container = tk.Frame(self.root, bg=Config.BACKGROUND_COLOR)
        self.main_container.pack(fill="both", expand=True)
        
        # Header
        self.create_header()
        
        # Content area
        self.create_content_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the header with navigation and user controls"""
        header_frame = tk.Frame(self.main_container, bg=Config.PRIMARY_COLOR, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # App title
        title_label = tk.Label(
            header_content,
            text=Config.APP_NAME,
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side="left")
        
        # Right side controls
        right_frame = tk.Frame(header_content, bg=Config.PRIMARY_COLOR)
        right_frame.pack(side="right")
        
        # Admin access button
        admin_btn = ModernButton(
            right_frame,
            text="Admin",
            command=self.show_admin_auth,
            style="outline",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            padx=10,
            pady=5
        )
        admin_btn.pack(side="right", padx=(0, 10))
        
        # User info and login/logout
        self.user_frame = tk.Frame(right_frame, bg=Config.PRIMARY_COLOR)
        self.user_frame.pack(side="right", padx=(20, 0))
        
        self.update_user_display()
        
        # Navigation buttons
        nav_frame = tk.Frame(header_content, bg=Config.PRIMARY_COLOR)
        nav_frame.pack(side="left", padx=(40, 0))
        
        # Sale/Rent toggle
        self.sale_btn = ModernButton(
            nav_frame,
            text="For Sale",
            command=lambda: self.switch_listing_type("sale"),
            style="secondary" if self.current_listing_type == "sale" else "outline"
        )
        self.sale_btn.pack(side="left", padx=(0, 10))
        
        self.rent_btn = ModernButton(
            nav_frame,
            text="For Rent",
            command=lambda: self.switch_listing_type("rent"),
            style="secondary" if self.current_listing_type == "rent" else "outline"
        )
        self.rent_btn.pack(side="left")
    
    def create_content_area(self):
        """Create the main content area"""
        # Content container
        content_frame = tk.Frame(self.main_container, bg=Config.BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search and filters
        self.search_filter = SearchFilter(
            content_frame,
            on_filter_change=self.apply_filters
        )
        self.search_filter.pack(fill="x", pady=(0, 20))
        
        # Properties list container
        self.properties_container = tk.Frame(content_frame, bg=Config.BACKGROUND_COLOR)
        self.properties_container.pack(fill="both", expand=True)
        
        # Create scrollable frame for properties
        self.create_scrollable_properties()
    
    def create_scrollable_properties(self):
        """Create scrollable frame for property listings with grid layout"""
        # Canvas and scrollbar
        canvas = tk.Canvas(self.properties_container, bg=Config.BACKGROUND_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.properties_container, orient="vertical", command=canvas.yview)
        
        self.properties_frame = tk.Frame(canvas, bg=Config.BACKGROUND_COLOR)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.properties_frame, anchor="nw")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region when frame changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update canvas window width to match canvas width
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas.create_window((0, 0), window=self.properties_frame, anchor="nw"), width=canvas_width)
        
        self.properties_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Store references
        self.canvas = canvas
        self.scrollbar = scrollbar
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.main_container, bg=Config.BORDER_COLOR, height=25)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BORDER_COLOR,
            fg=Config.TEXT_SECONDARY,
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=2)
    
    def update_user_display(self):
        """Update user display in header"""
        # Clear existing widgets
        for widget in self.user_frame.winfo_children():
            widget.destroy()
        
        if self.current_user:
            # User info
            user_info_label = tk.Label(
                self.user_frame,
                text=f"Welcome, {self.current_user['first_name']}!",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.PRIMARY_COLOR,
                fg="white"
            )
            user_info_label.pack(side="left", padx=(0, 10))
            
            # Logout button
            logout_btn = ModernButton(
                self.user_frame,
                text="Logout",
                command=self.logout,
                style="outline"
            )
            logout_btn.pack(side="left")
        else:
            # Login button
            login_btn = ModernButton(
                self.user_frame,
                text="Login / Sign Up",
                command=self.show_auth_window,
                style="outline"
            )
            login_btn.pack(side="left")
    
    def show_auth_window(self):
        """Show authentication window"""
        AuthWindow(self.root, self.db_manager, self.on_login_success)
    
    def show_admin_auth(self):
        """Show admin authentication window"""
        AdminAuthWindow(self.root, self.db_manager, self.on_admin_login_success)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.update_user_display()
        self.update_status(f"Logged in as {user['first_name']}")
    
    def on_admin_login_success(self, admin):
        """Handle successful admin login"""
        AdminDashboard(self.root, self.db_manager, admin)
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.update_user_display()
        self.update_status("Logged out")
    
    def switch_listing_type(self, listing_type):
        """Switch between sale and rent listings"""
        self.current_listing_type = listing_type
        
        # Update button styles
        if listing_type == "sale":
            self.sale_btn.configure(bg=Config.SECONDARY_COLOR)
            self.rent_btn.configure(bg="white", fg=Config.PRIMARY_COLOR)
        else:
            self.rent_btn.configure(bg=Config.SECONDARY_COLOR)
            self.sale_btn.configure(bg="white", fg=Config.PRIMARY_COLOR)
        
        self.load_properties()
    
    def apply_filters(self, filters):
        """Apply search filters"""
        self.current_filters = filters
        self.load_properties()
    
    def load_properties(self):
        """Load and display properties in a 3-column grid"""
        # Clear existing properties
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        
        # Get properties from database
        properties = self.db_manager.get_properties(
            listing_type=self.current_listing_type,
            filters=self.current_filters
        )
        
        if not properties:
            # No properties found
            no_props_label = tk.Label(
                self.properties_frame,
                text="No properties found matching your criteria.",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
                bg=Config.BACKGROUND_COLOR,
                fg=Config.TEXT_SECONDARY
            )
            no_props_label.grid(row=0, column=0, columnspan=3, pady=50)
            self.update_status("No properties found")
            return
        
        # Configure grid columns to be equal width
        self.properties_frame.columnconfigure(0, weight=1, uniform="column")
        self.properties_frame.columnconfigure(1, weight=1, uniform="column")
        self.properties_frame.columnconfigure(2, weight=1, uniform="column")
        
        # Display properties in 3-column grid
        for i, property_data in enumerate(properties):
            row = i // 3
            col = i % 3
            
            # Create property card with fixed width for grid consistency
            property_card = PropertyCard(
                self.properties_frame,
                property_data,
                on_click=self.handle_property_action,
                width=350,  # Fixed width for consistent grid
                height=280  # Fixed height for consistent grid
            )
            
            # Grid the property card with padding
            property_card.grid(
                row=row, 
                column=col, 
                padx=10, 
                pady=10, 
                sticky="ew"
            )
            
            # Prevent the card from shrinking
            property_card.grid_propagate(False)
        
        # Update status
        self.update_status(f"Found {len(properties)} properties")
        
        # Update canvas scroll region
        self.properties_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def handle_property_action(self, property_data, action_type="view"):
        """Handle property actions (view details or quick transaction)"""
        if action_type == "transaction":
            # Quick transaction action
            if not self.current_user:
                messagebox.showwarning("Login Required", "Please log in to perform this action.")
                self.show_auth_window()
                return
            
            # Open property details window with transaction focus
            details_window = PropertyDetailsWindow(self.root, property_data, self.db_manager, self.current_user)
            
            # Automatically trigger the appropriate transaction
            if property_data['listing_type'] == 'sale':
                # Small delay to ensure window is fully loaded
                self.root.after(100, details_window.handle_purchase)
            else:
                self.root.after(100, details_window.handle_rent)
        
        else:
            # View details action
            PropertyDetailsWindow(self.root, property_data, self.db_manager, self.current_user)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        
        # Auto-clear status after 5 seconds
        self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
    
    def run(self):
        """Run the application"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (Config.WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (Config.WINDOW_HEIGHT // 2)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}+{x}+{y}")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = RealEstateApp()
    app.run()