import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, PropertyCard
from config import Config

class FavoritesWindow:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("My Favorites")
        self.window.geometry("1200x800")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_favorites()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            header_content,
            text="My Favorite Properties",
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side="left")
        
        # Close button
        close_btn = ModernButton(
            header_content,
            text="Close",
            command=self.window.destroy,
            style="outline"
        )
        close_btn.pack(side="right")
        
        # Main content area
        content_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create scrollable frame for favorites
        self.create_scrollable_favorites(content_frame)
    
    def create_scrollable_favorites(self, parent):
        """Create scrollable frame for favorite properties"""
        # Canvas and scrollbar
        canvas = tk.Canvas(parent, bg=Config.BACKGROUND_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        self.favorites_frame = tk.Frame(canvas, bg=Config.BACKGROUND_COLOR)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.favorites_frame, anchor="nw")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region when frame changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas.create_window((0, 0), window=self.favorites_frame, anchor="nw"), width=canvas_width)
        
        self.favorites_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Store references
        self.canvas = canvas
    
    def load_favorites(self):
        """Load and display favorite properties"""
        # Clear existing favorites
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get favorite properties with full details
            favorites = self.get_detailed_favorites()
            
            if not favorites:
                # No favorites found
                no_favorites_label = tk.Label(
                    self.favorites_frame,
                    text="You haven't added any properties to your favorites yet.\n\nBrowse properties and click 'Add to Favorites' to see them here.",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
                    bg=Config.BACKGROUND_COLOR,
                    fg=Config.TEXT_SECONDARY,
                    justify="center"
                )
                no_favorites_label.pack(expand=True, pady=100)
                return
            
            # Configure grid columns
            self.favorites_frame.columnconfigure(0, weight=1, uniform="column")
            self.favorites_frame.columnconfigure(1, weight=1, uniform="column")
            self.favorites_frame.columnconfigure(2, weight=1, uniform="column")
            
            # Display favorites in 3-column grid
            for i, property_data in enumerate(favorites):
                row = i // 3
                col = i % 3
                
                # Create property card
                property_card = PropertyCard(
                    self.favorites_frame,
                    property_data,
                    on_click=self.handle_property_action,
                    width=350,
                    height=280
                )
                
                # Grid the property card
                property_card.grid(
                    row=row,
                    column=col,
                    padx=10,
                    pady=10,
                    sticky="ew"
                )
                
                # Add remove from favorites button
                remove_btn = ModernButton(
                    property_card,
                    text="Remove from Favorites",
                    command=lambda prop_id=property_data['id']: self.remove_favorite(prop_id),
                    style="outline",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                    padx=5,
                    pady=3
                )
                remove_btn.pack(side="bottom", pady=(5, 10))
            
            # Update canvas scroll region
            self.favorites_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load favorites: {str(e)}")
    
    def get_detailed_favorites(self):
        """Get detailed information for favorite properties"""
        try:
            # Get basic favorite info
            basic_favorites = self.db_manager.get_user_favorites(self.current_user['id'])
            
            # Get full property details for each favorite
            detailed_favorites = []
            for fav in basic_favorites:
                property_details = self.db_manager.get_property_by_id(fav['id'])
                if property_details and property_details['status'] == 'available':
                    detailed_favorites.append(property_details)
            
            return detailed_favorites
            
        except Exception as e:
            print(f"Error getting detailed favorites: {e}")
            return []
    
    def handle_property_action(self, property_data, action_type="view"):
        """Handle property actions from favorites"""
        if action_type == "view":
            # Import here to avoid circular imports
            from property_details import PropertyDetailsWindow
            PropertyDetailsWindow(self.window, property_data, self.db_manager, self.current_user)
        elif action_type == "transaction":
            # Handle quick transaction
            from property_details import PropertyDetailsWindow
            details_window = PropertyDetailsWindow(self.window, property_data, self.db_manager, self.current_user)
            
            # Automatically trigger the appropriate transaction
            if property_data['listing_type'] == 'sale':
                self.window.after(100, details_window.handle_purchase)
            else:
                self.window.after(100, details_window.handle_rent)
    
    def remove_favorite(self, property_id):
        """Remove property from favorites"""
        result = messagebox.askyesno(
            "Remove Favorite",
            "Are you sure you want to remove this property from your favorites?"
        )
        
        if result:
            success = self.db_manager.remove_from_favorites(
                self.current_user['id'],
                property_id
            )
            
            if success:
                messagebox.showinfo("Success", "Property removed from favorites")
                self.load_favorites()  # Refresh the list
            else:
                messagebox.showerror("Error", "Failed to remove from favorites")