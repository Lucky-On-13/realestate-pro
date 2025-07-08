import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from image_manager import ImageManager

class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        # Color schemes for different button styles
        styles = {
            "primary": {
                "bg": Config.PRIMARY_COLOR,
                "fg": "white",
                "activebackground": "#1E5A73",
                "activeforeground": "white"
            },
            "secondary": {
                "bg": Config.SECONDARY_COLOR,
                "fg": "white",
                "activebackground": "#7A2B56",
                "activeforeground": "white"
            },
            "accent": {
                "bg": Config.ACCENT_COLOR,
                "fg": "white",
                "activebackground": "#D17701",
                "activeforeground": "white"
            },
            "success": {
                "bg": Config.SUCCESS_COLOR,
                "fg": "white",
                "activebackground": "#A82A1A",
                "activeforeground": "white"
            },
            "outline": {
                "bg": "white",
                "fg": Config.PRIMARY_COLOR,
                "activebackground": Config.BACKGROUND_COLOR,
                "activeforeground": Config.PRIMARY_COLOR,
                "relief": "solid",
                "borderwidth": 2
            }
        }
        
        style_config = styles.get(style, styles["primary"])
        
        # Merge style_config with kwargs, giving priority to kwargs
        button_config = {
            "font": (Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "padx": 20,
            "pady": 10
        }
        button_config.update(style_config)
        button_config.update(kwargs)
        
        super().__init__(
            parent,
            text=text,
            command=command,
            **button_config
        )
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.original_bg = self.cget("bg")
        self.original_fg = self.cget("fg")
    
    def on_enter(self, event):
        self.configure(bg=self.cget("activebackground"))
    
    def on_leave(self, event):
        self.configure(bg=self.original_bg)

class ModernEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        # Prepare entry configuration
        entry_config = {
            "font": (Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            "relief": "solid",
            "borderwidth": 2,
            "fg": Config.TEXT_PRIMARY,
            "bg": "white",
            "insertbackground": Config.PRIMARY_COLOR
        }
        entry_config.update(kwargs)
        
        super().__init__(parent, **entry_config)
        
        self.placeholder = placeholder
        self.placeholder_color = Config.TEXT_SECONDARY
        self.default_fg_color = Config.TEXT_PRIMARY
        
        if placeholder:
            self.put_placeholder()
        
        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)
    
    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self.configure(fg=self.placeholder_color)
    
    def focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=self.default_fg_color)
    
    def focus_out(self, event):
        if not self.get():
            self.put_placeholder()
    
    def get_value(self):
        value = self.get()
        return value if value != self.placeholder else ""

class PropertyCard(tk.Frame):
    def __init__(self, parent, property_data, on_click=None, **kwargs):
        # Prepare frame configuration
        frame_config = {
            "bg": Config.CARD_COLOR,
            "relief": "solid",
            "borderwidth": 1
        }
        frame_config.update(kwargs)
        
        super().__init__(parent, **frame_config)
        
        self.property_data = property_data
        self.on_click = on_click
        self.image_manager = ImageManager()
        
        self.create_widgets()
        self.bind_events()
    
    def create_widgets(self):
        # Main container with padding
        main_frame = tk.Frame(self, bg=Config.CARD_COLOR)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Property image
        image_frame = tk.Frame(main_frame, bg=Config.BORDER_COLOR, height=120)
        image_frame.pack(fill="x", pady=(0, 10))
        image_frame.pack_propagate(False)
        
        # Load and display property image
        try:
            primary_image = self.property_data.get('primary_image')
            if primary_image:
                img = self.image_manager.load_image_for_display(
                    primary_image, 
                    size=(320, 120),
                    thumbnail=True
                )
                
                image_label = tk.Label(
                    image_frame,
                    image=img,
                    bg="white"
                )
                image_label.pack(expand=True)
                # Keep reference to prevent garbage collection
                image_label.image = img
            else:
                # Placeholder if no image
                image_label = tk.Label(
                    image_frame,
                    text="📷 No Image",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                    bg=Config.BORDER_COLOR,
                    fg=Config.TEXT_SECONDARY
                )
                image_label.pack(expand=True)
        except Exception as e:
            print(f"Error loading property image: {e}")
            # Fallback placeholder
            image_label = tk.Label(
                image_frame,
                text="📷 Image Error",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                bg=Config.BORDER_COLOR,
                fg=Config.TEXT_SECONDARY
            )
            image_label.pack(expand=True)
        
        # Title (truncated if too long)
        title_text = self.property_data['title']
        if len(title_text) > 25:
            title_text = title_text[:22] + "..."
        
        title_label = tk.Label(
            main_frame,
            text=title_text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 5))
        
        # Price
        price_text = f"${self.property_data['price']:,.0f}"
        if self.property_data['listing_type'] == 'rent':
            price_text += "/mo"
        
        price_label = tk.Label(
            main_frame,
            text=price_text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.PRIMARY_COLOR,
            anchor="w"
        )
        price_label.pack(fill="x", pady=(0, 5))
        
        # Property details (compact)
        details_text = f"{self.property_data['bedrooms']}bd • {self.property_data['bathrooms']}ba • {self.property_data['square_feet']} sqft"
        details_label = tk.Label(
            main_frame,
            text=details_text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_SECONDARY,
            anchor="w"
        )
        details_label.pack(fill="x", pady=(0, 5))
        
        # Location (truncated)
        location_text = f"{self.property_data['city']}, {self.property_data['state']}"
        if len(location_text) > 20:
            location_text = location_text[:17] + "..."
        
        location_label = tk.Label(
            main_frame,
            text=location_text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_SECONDARY,
            anchor="w"
        )
        location_label.pack(fill="x", pady=(0, 10))
        
        # Action buttons (smaller for grid layout)
        button_frame = tk.Frame(main_frame, bg=Config.CARD_COLOR)
        button_frame.pack(fill="x")
        
        # View Details button (smaller)
        view_btn = ModernButton(
            button_frame,
            text="Details",
            command=lambda: self.on_click(self.property_data, action_type="view") if self.on_click else None,
            style="primary",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
            padx=8,
            pady=5
        )
        view_btn.pack(side="left", padx=(0, 5))
        
        # Quick action button (smaller)
        action_text = "Buy" if self.property_data['listing_type'] == 'sale' else "Rent"
        action_style = "success" if self.property_data['listing_type'] == 'sale' else "accent"
        
        action_btn = ModernButton(
            button_frame,
            text=action_text,
            command=lambda: self.on_click(self.property_data, action_type="transaction") if self.on_click else None,
            style=action_style,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
            padx=8,
            pady=5
        )
        action_btn.pack(side="left")
    
    def bind_events(self):
        # Make the entire card clickable for viewing details (except buttons)
        def on_card_click(event):
            # Check if click was on a button
            widget = event.widget
            if isinstance(widget, ModernButton):
                return
            
            if self.on_click:
                self.on_click(self.property_data, action_type="view")
        
        # Bind click event to card and non-button children
        self.bind("<Button-1>", on_card_click)
        self.bind_click_to_children(self, on_card_click)
    
    def bind_click_to_children(self, widget, callback):
        """Recursively bind click event to non-button children"""
        for child in widget.winfo_children():
            if not isinstance(child, ModernButton):
                child.bind("<Button-1>", callback)
                self.bind_click_to_children(child, callback)

class SearchFilter(tk.Frame):
    def __init__(self, parent, on_filter_change=None, **kwargs):
        frame_config = {"bg": Config.BACKGROUND_COLOR}
        frame_config.update(kwargs)
        
        super().__init__(parent, **frame_config)
        
        self.on_filter_change = on_filter_change
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self,
            text="Search & Filter",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        title_label.pack(pady=(0, 10))
        
        # Filter frame
        filter_frame = tk.Frame(self, bg=Config.BACKGROUND_COLOR)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Location search
        location_label = tk.Label(
            filter_frame,
            text="Location:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        location_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        self.location_entry = ModernEntry(filter_frame, placeholder="Enter city")
        self.location_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        
        # Property type
        type_label = tk.Label(
            filter_frame,
            text="Type:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        type_label.grid(row=0, column=2, sticky="w", padx=(0, 5))
        
        self.type_var = tk.StringVar(value="")
        type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.type_var,
            values=["", "House", "Apartment", "Condo", "Loft"],
            state="readonly",
            width=10
        )
        type_combo.grid(row=0, column=3, padx=(0, 10))
        
        # Price range
        price_label = tk.Label(
            filter_frame,
            text="Price Range:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        price_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        
        price_frame = tk.Frame(filter_frame, bg=Config.BACKGROUND_COLOR)
        price_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.min_price_entry = ModernEntry(price_frame, placeholder="Min price", width=10)
        self.min_price_entry.pack(side="left", padx=(0, 5))
        
        tk.Label(price_frame, text="to", bg=Config.BACKGROUND_COLOR).pack(side="left", padx=5)
        
        self.max_price_entry = ModernEntry(price_frame, placeholder="Max price", width=10)
        self.max_price_entry.pack(side="left", padx=(5, 0))
        
        # Bedrooms
        bed_label = tk.Label(
            filter_frame,
            text="Min Bedrooms:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        bed_label.grid(row=1, column=3, sticky="w", padx=(10, 5), pady=(10, 0))
        
        self.bedrooms_var = tk.StringVar(value="")
        bedrooms_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.bedrooms_var,
            values=["", "1", "2", "3", "4", "5+"],
            state="readonly",
            width=5
        )
        bedrooms_combo.grid(row=1, column=4, pady=(10, 0))
        
        # Configure grid weights
        filter_frame.columnconfigure(1, weight=1)
        
        # Apply filter button
        apply_btn = ModernButton(
            self,
            text="Apply Filters",
            command=self.apply_filters,
            style="primary"
        )
        apply_btn.pack(pady=(10, 0))
    
    def apply_filters(self):
        if self.on_filter_change:
            filters = {
                'city': self.location_entry.get_value(),
                'property_type': self.type_var.get() if self.type_var.get() else None,
                'min_price': float(self.min_price_entry.get_value()) if self.min_price_entry.get_value() else None,
                'max_price': float(self.max_price_entry.get_value()) if self.max_price_entry.get_value() else None,
                'bedrooms': int(self.bedrooms_var.get()) if self.bedrooms_var.get() and self.bedrooms_var.get() != "5+" else None
            }
            self.on_filter_change(filters)
    
    def clear_filters(self):
        self.location_entry.delete(0, tk.END)
        self.type_var.set("")
        self.min_price_entry.delete(0, tk.END)
        self.max_price_entry.delete(0, tk.END)
        self.bedrooms_var.set("")
        if self.on_filter_change:
            self.on_filter_change({})