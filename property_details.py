import tkinter as tk
from tkinter import messagebox
from ui_components import ModernButton
from config import Config
from image_manager import ImageManager, ImageGalleryWidget

class PropertyDetailsWindow:
    def __init__(self, parent, property_data, db_manager, current_user=None):
        self.parent = parent
        self.property_data = property_data
        self.db_manager = db_manager
        self.current_user = current_user
        self.image_manager = ImageManager()
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Property Details - {property_data['title']}")
        self.window.geometry("900x700")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create scrollable main container
        canvas = tk.Canvas(self.window, bg=Config.BACKGROUND_COLOR)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        
        main_frame = tk.Frame(canvas, bg=Config.BACKGROUND_COLOR)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region when frame changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas.create_window((0, 0), window=main_frame, anchor="nw"), width=canvas_width)
        
        main_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Content with padding
        content_frame = tk.Frame(main_frame, bg=Config.BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Image gallery section
        self.create_image_section(content_frame)
        
        # Title section
        title_frame = tk.Frame(content_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_content = tk.Frame(title_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        title_content.pack(fill="both", expand=True)
        
        # Property title
        title_label = tk.Label(
            title_content,
            text=self.property_data['title'],
            font=(Config.FONT_FAMILY, 20, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x")
        
        # Price
        price_text = f"${self.property_data['price']:,.0f}"
        if self.property_data['listing_type'] == 'rent':
            price_text += "/month"
        
        price_label = tk.Label(
            title_content,
            text=price_text,
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.PRIMARY_COLOR,
            anchor="w"
        )
        price_label.pack(fill="x", pady=(5, 0))
        
        # Address
        address_text = f"{self.property_data['address']}, {self.property_data['city']}, {self.property_data['state']} {self.property_data['zip_code']}"
        address_label = tk.Label(
            title_content,
            text=address_text,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_SECONDARY,
            anchor="w"
        )
        address_label.pack(fill="x", pady=(5, 0))
        
        # Property details section
        details_frame = tk.Frame(content_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        details_frame.pack(fill="x", pady=(0, 20))
        
        details_content = tk.Frame(details_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        details_content.pack(fill="both", expand=True)
        
        # Details header
        details_header = tk.Label(
            details_content,
            text="Property Details",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        details_header.pack(fill="x", pady=(0, 15))
        
        # Create details grid
        details_grid = tk.Frame(details_content, bg=Config.CARD_COLOR)
        details_grid.pack(fill="x")
        
        # Property details data
        details_data = [
            ("Property Type", self.property_data['property_type']),
            ("Bedrooms", str(self.property_data['bedrooms'])),
            ("Bathrooms", str(self.property_data['bathrooms'])),
            ("Square Feet", f"{self.property_data['square_feet']:,}"),
            ("Lot Size", f"{self.property_data['lot_size']} acres" if self.property_data['lot_size'] else "N/A"),
            ("Year Built", str(self.property_data['year_built'])),
            ("Listing Type", self.property_data['listing_type'].title()),
            ("Status", self.property_data['status'].title())
        ]
        
        for i, (label, value) in enumerate(details_data):
            row = i // 2
            col = i % 2
            
            detail_frame = tk.Frame(details_grid, bg=Config.CARD_COLOR)
            detail_frame.grid(row=row, column=col, sticky="ew", padx=(0, 20), pady=5)
            
            tk.Label(
                detail_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                detail_frame,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left", padx=(10, 0))
        
        # Configure grid weights
        details_grid.columnconfigure(0, weight=1)
        details_grid.columnconfigure(1, weight=1)
        
        # Description section
        if self.property_data['description']:
            desc_frame = tk.Frame(content_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
            desc_frame.pack(fill="x", pady=(0, 20))
            
            desc_content = tk.Frame(desc_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
            desc_content.pack(fill="both", expand=True)
            
            desc_header = tk.Label(
                desc_content,
                text="Description",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            )
            desc_header.pack(fill="x", pady=(0, 10))
            
            desc_text = tk.Label(
                desc_content,
                text=self.property_data['description'],
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w",
                wraplength=800,
                justify="left"
            )
            desc_text.pack(fill="x")
        
        # Agent information
        agent_frame = tk.Frame(content_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        agent_frame.pack(fill="x", pady=(0, 20))
        
        agent_content = tk.Frame(agent_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        agent_content.pack(fill="both", expand=True)
        
        agent_header = tk.Label(
            agent_content,
            text="Agent Information",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        agent_header.pack(fill="x", pady=(0, 10))
        
        agent_info_frame = tk.Frame(agent_content, bg=Config.CARD_COLOR)
        agent_info_frame.pack(fill="x")
        
        # Agent details
        agent_details = [
            ("Name", self.property_data['agent_name']),
            ("Phone", self.property_data['agent_phone']),
            ("Email", self.property_data['agent_email'])
        ]
        
        for label, value in agent_details:
            detail_frame = tk.Frame(agent_info_frame, bg=Config.CARD_COLOR)
            detail_frame.pack(fill="x", pady=2)
            
            tk.Label(
                detail_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w",
                width=8
            ).pack(side="left")
            
            tk.Label(
                detail_frame,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left", padx=(10, 0))
        
        # Action buttons
        action_frame = tk.Frame(content_frame, bg=Config.BACKGROUND_COLOR)
        action_frame.pack(fill="x", pady=(20, 0))
        
        if self.current_user:
            if self.property_data['listing_type'] == 'sale':
                purchase_btn = ModernButton(
                    action_frame,
                    text="Purchase Property",
                    command=self.handle_purchase,
                    style="success"
                )
                purchase_btn.pack(side="left", padx=(0, 10))
            else:
                rent_btn = ModernButton(
                    action_frame,
                    text="Rent Property",
                    command=self.handle_rent,
                    style="accent"
                )
                rent_btn.pack(side="left", padx=(0, 10))
            
            # Check if already in favorites
            is_favorite = self.db_manager.is_favorite(self.current_user['id'], self.property_data['id'])
            favorite_text = "Remove from Favorites" if is_favorite else "Add to Favorites"
            favorite_style = "outline" if not is_favorite else "secondary"
            
            self.favorite_btn = ModernButton(
                action_frame,
                text=favorite_text,
                command=self.handle_favorite,
                style=favorite_style
            )
            self.favorite_btn.pack(side="left", padx=(0, 10))
        else:
            # Show login prompt for non-logged users
            login_prompt = tk.Label(
                action_frame,
                text="Please log in to purchase, rent, or add to favorites",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.BACKGROUND_COLOR,
                fg=Config.TEXT_SECONDARY
            )
            login_prompt.pack(side="left")
        
        close_btn = ModernButton(
            action_frame,
            text="Close",
            command=self.window.destroy,
            style="outline"
        )
        close_btn.pack(side="right")
    
    def create_image_section(self, parent):
        """Create image gallery section"""
        image_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        image_frame.pack(fill="x", pady=(0, 20))
        
        # Main property image
        main_image_frame = tk.Frame(image_frame, bg=Config.CARD_COLOR)
        main_image_frame.pack(fill="x", padx=20, pady=20)
        
        # Load primary image
        try:
            primary_image = self.property_data.get('primary_image')
            if primary_image:
                img = self.image_manager.load_image_for_display(
                    primary_image, 
                    size=(600, 300)
                )
                
                image_label = tk.Label(
                    main_image_frame,
                    image=img,
                    bg="white",
                    relief="solid",
                    borderwidth=1
                )
                image_label.pack()
                # Keep reference to prevent garbage collection
                image_label.image = img
            else:
                # Placeholder if no image
                placeholder_label = tk.Label(
                    main_image_frame,
                    text="📷 No Images Available",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
                    bg=Config.BORDER_COLOR,
                    fg=Config.TEXT_SECONDARY,
                    width=60,
                    height=15
                )
                placeholder_label.pack()
        except Exception as e:
            print(f"Error loading main property image: {e}")
            # Error placeholder
            error_label = tk.Label(
                main_image_frame,
                text="📷 Error Loading Image",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
                bg=Config.BORDER_COLOR,
                fg=Config.TEXT_SECONDARY,
                width=60,
                height=15
            )
            error_label.pack()
        
        # Image gallery for additional images
        gallery_widget = ImageGalleryWidget(
            image_frame, 
            self.property_data['id'], 
            self.db_manager,
            bg=Config.CARD_COLOR
        )
        gallery_widget.pack(fill="x", padx=20, pady=(0, 20))
    
    def handle_purchase(self):
        """Handle property purchase"""
        if not self.current_user:
            messagebox.showerror("Error", "Please log in to purchase property")
            return
        
        # Check if property is still available
        if self.property_data['status'] != 'available':
            messagebox.showerror("Error", "This property is no longer available")
            return
        
        result = messagebox.askyesno(
            "Confirm Purchase",
            f"Are you sure you want to purchase this property for ${self.property_data['price']:,.0f}?\n\n"
            f"Property: {self.property_data['title']}\n"
            f"Address: {self.property_data['address']}, {self.property_data['city']}, {self.property_data['state']}\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            success = self.db_manager.create_transaction(
                self.property_data['id'],
                self.current_user['id'],
                self.property_data['owner_id'],
                'purchase',
                self.property_data['price'],
                f"Purchase of {self.property_data['title']} by {self.current_user['first_name']} {self.current_user['last_name']}"
            )
            
            if success:
                messagebox.showinfo(
                    "Purchase Successful!", 
                    f"Congratulations! You have successfully purchased:\n\n"
                    f"{self.property_data['title']}\n"
                    f"Amount: ${self.property_data['price']:,.0f}\n\n"
                    f"Transaction details have been recorded.\n"
                    f"You will be contacted by the agent for next steps."
                )
                self.window.destroy()
                # Refresh the main window to update property status
                if hasattr(self.parent, 'load_properties'):
                    self.parent.load_properties()
            else:
                messagebox.showerror("Error", "Failed to complete purchase. Please try again or contact support.")
    
    def handle_rent(self):
        """Handle property rental"""
        if not self.current_user:
            messagebox.showerror("Error", "Please log in to rent property")
            return
        
        # Check if property is still available
        if self.property_data['status'] != 'available':
            messagebox.showerror("Error", "This property is no longer available")
            return
        
        result = messagebox.askyesno(
            "Confirm Rental",
            f"Are you sure you want to rent this property for ${self.property_data['price']:,.0f}/month?\n\n"
            f"Property: {self.property_data['title']}\n"
            f"Address: {self.property_data['address']}, {self.property_data['city']}, {self.property_data['state']}\n\n"
            f"You will need to sign a lease agreement with the property owner."
        )
        
        if result:
            success = self.db_manager.create_transaction(
                self.property_data['id'],
                self.current_user['id'],
                self.property_data['owner_id'],
                'rent',
                self.property_data['price'],
                f"Rental of {self.property_data['title']} by {self.current_user['first_name']} {self.current_user['last_name']}"
            )
            
            if success:
                messagebox.showinfo(
                    "Rental Application Successful!", 
                    f"Great! Your rental application has been submitted for:\n\n"
                    f"{self.property_data['title']}\n"
                    f"Monthly Rent: ${self.property_data['price']:,.0f}\n\n"
                    f"The property owner will contact you soon to discuss\n"
                    f"lease terms and schedule a viewing."
                )
                self.window.destroy()
                # Refresh the main window to update property status
                if hasattr(self.parent, 'load_properties'):
                    self.parent.load_properties()
            else:
                messagebox.showerror("Error", "Failed to submit rental application. Please try again or contact support.")
    
    def handle_favorite(self):
        """Handle adding to favorites"""
        if not self.current_user:
            messagebox.showerror("Error", "Please log in to add favorites")
            return
        
        # Check current favorite status
        is_favorite = self.db_manager.is_favorite(self.current_user['id'], self.property_data['id'])
        
        if is_favorite:
            # Remove from favorites
            success = self.db_manager.remove_from_favorites(
                self.current_user['id'],
                self.property_data['id']
            )
            
            if success:
                messagebox.showinfo("Success", f"'{self.property_data['title']}' has been removed from your favorites!")
                self.favorite_btn.configure(text="Add to Favorites", bg=Config.PRIMARY_COLOR)
            else:
                messagebox.showerror("Error", "Failed to remove from favorites")
        else:
            # Add to favorites
            success = self.db_manager.add_to_favorites(
                self.current_user['id'],
                self.property_data['id']
            )
            
            if success:
                messagebox.showinfo("Success", f"'{self.property_data['title']}' has been added to your favorites!")
                self.favorite_btn.configure(text="Remove from Favorites", bg=Config.SECONDARY_COLOR)
            else:
                messagebox.showerror("Error", "This property is already in your favorites")