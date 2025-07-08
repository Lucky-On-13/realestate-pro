import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, ModernEntry
from config import Config
from image_manager import ImageUploadWidget, ImageGalleryWidget

class PropertyManagementWindow:
    def __init__(self, parent, db_manager, admin_user):
        self.parent = parent
        self.db_manager = db_manager
        self.admin_user = admin_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Property Management")
        self.window.geometry("1200x800")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        self.selected_property = None
        
        self.create_widgets()
        self.load_properties()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        title_label = tk.Label(
            header_content,
            text="Property Management",
            font=(Config.FONT_FAMILY, 16, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side="left")
        
        close_btn = ModernButton(
            header_content,
            text="Close",
            command=self.window.destroy,
            style="outline"
        )
        close_btn.pack(side="right")
        
        # Main content
        main_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Property list
        left_panel = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Property list header
        list_header = tk.Frame(left_panel, bg=Config.CARD_COLOR)
        list_header.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            list_header,
            text="Properties",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        ).pack(side="left")
        
        refresh_btn = ModernButton(
            list_header,
            text="Refresh",
            command=self.load_properties,
            style="outline",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            padx=10,
            pady=5
        )
        refresh_btn.pack(side="right")
        
        # Properties treeview
        tree_frame = tk.Frame(left_panel, bg=Config.CARD_COLOR)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview with scrollbar
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Type", "Price", "Status"), show="headings")
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=200)
        self.tree.column("Type", width=100)
        self.tree.column("Price", width=100)
        self.tree.column("Status", width=100)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_property_select)
        
        # Right panel - Property details and actions
        right_panel = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1, width=400)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Details header
        details_header = tk.Label(
            right_panel,
            text="Property Details",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        details_header.pack(pady=10)
        
        # Details content
        self.details_frame = tk.Frame(right_panel, bg=Config.CARD_COLOR)
        self.details_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Action buttons
        actions_frame = tk.Frame(right_panel, bg=Config.CARD_COLOR)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.edit_btn = ModernButton(
            actions_frame,
            text="Edit Property",
            command=self.edit_property,
            style="primary"
        )
        self.edit_btn.pack(fill="x", pady=(0, 10))
        
        self.delete_btn = ModernButton(
            actions_frame,
            text="Delete Property",
            command=self.delete_property,
            style="outline"
        )
        self.delete_btn.pack(fill="x", pady=(0, 10))
        
        self.add_btn = ModernButton(
            actions_frame,
            text="Add New Property",
            command=self.add_property,
            style="success"
        )
        self.add_btn.pack(fill="x")
        
        # Initially disable edit/delete buttons
        self.edit_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
    
    def load_properties(self):
        """Load all properties into the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            properties = self.db_manager.get_all_properties_admin()
            
            for prop in properties:
                price_text = f"${prop['price']:,.0f}"
                if prop['listing_type'] == 'rent':
                    price_text += "/mo"
                
                self.tree.insert("", "end", values=(
                    prop['id'],
                    prop['title'][:30] + "..." if len(prop['title']) > 30 else prop['title'],
                    prop['property_type'],
                    price_text,
                    prop['status'].title()
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load properties: {str(e)}")
    
    def on_property_select(self, event):
        """Handle property selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            property_id = item['values'][0]
            
            # Get full property details
            self.selected_property = self.db_manager.get_property_by_id_admin(property_id)
            
            if self.selected_property:
                self.display_property_details()
                self.edit_btn.configure(state="normal")
                self.delete_btn.configure(state="normal")
    
    def display_property_details(self):
        """Display selected property details"""
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_property:
            return
        
        prop = self.selected_property
        
        # Property details
        details = [
            ("ID", str(prop['id'])),
            ("Title", prop['title']),
            ("Type", prop['property_type']),
            ("Address", prop['address']),
            ("City", prop['city']),
            ("State", prop['state']),
            ("ZIP", prop['zip_code']),
            ("Price", f"${prop['price']:,.0f}"),
            ("Bedrooms", str(prop['bedrooms'])),
            ("Bathrooms", str(prop['bathrooms'])),
            ("Sq Ft", f"{prop['square_feet']:,}"),
            ("Lot Size", f"{prop['lot_size']} acres" if prop['lot_size'] else "N/A"),
            ("Year Built", str(prop['year_built'])),
            ("Listing Type", prop['listing_type'].title()),
            ("Status", prop['status'].title()),
            ("Owner", prop.get('owner_name', 'N/A')),
            ("Agent", prop.get('agent_name', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details):
            detail_frame = tk.Frame(self.details_frame, bg=Config.CARD_COLOR)
            detail_frame.pack(fill="x", pady=2)
            
            tk.Label(
                detail_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                width=12,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                detail_frame,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w",
                wraplength=200
            ).pack(side="left", padx=(5, 0))
        
        # Description
        if prop.get('description'):
            desc_frame = tk.Frame(self.details_frame, bg=Config.CARD_COLOR)
            desc_frame.pack(fill="x", pady=(10, 0))
            
            tk.Label(
                desc_frame,
                text="Description:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x")
            
            tk.Label(
                desc_frame,
                text=prop['description'],
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w",
                wraplength=350,
                justify="left"
            ).pack(fill="x", pady=(5, 0))
    
    def edit_property(self):
        """Open property edit dialog"""
        if not self.selected_property:
            return
        
        PropertyEditDialog(self.window, self.db_manager, self.selected_property, self.on_property_updated)
    
    def delete_property(self):
        """Delete selected property"""
        if not self.selected_property:
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the property:\n\n"
            f"'{self.selected_property['title']}'?\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            try:
                success = self.db_manager.delete_property(self.selected_property['id'])
                if success:
                    messagebox.showinfo("Success", "Property deleted successfully")
                    self.load_properties()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", "Failed to delete property")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete property: {str(e)}")
    
    def add_property(self):
        """Open add property dialog"""
        PropertyEditDialog(self.window, self.db_manager, None, self.on_property_updated)
    
    def on_property_updated(self):
        """Callback when property is updated/added"""
        self.load_properties()
        self.clear_details()
    
    def clear_details(self):
        """Clear property details"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        self.selected_property = None
        self.edit_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")

class PropertyEditDialog:
    def __init__(self, parent, db_manager, property_data, on_success_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.property_data = property_data
        self.on_success_callback = on_success_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Property" if property_data else "Add Property")
        self.window.geometry("800x800")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.uploaded_images = []
        
        self.create_widgets()
        if property_data:
            self.populate_fields()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_text = "Edit Property" if self.property_data else "Add New Property"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=(Config.FONT_FAMILY, 14, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=10)
        
        # Scrollable form
        canvas = tk.Canvas(self.window, bg=Config.BACKGROUND_COLOR)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        
        self.form_frame = tk.Frame(canvas, bg=Config.BACKGROUND_COLOR)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        self.create_form_fields()
        
        # Update scroll region
        self.form_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        save_btn = ModernButton(
            button_frame,
            text="Save Property",
            command=self.save_property,
            style="success"
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ModernButton(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            style="outline"
        )
        cancel_btn.pack(side="left")
    
    def create_form_fields(self):
        """Create form fields"""
        form_content = tk.Frame(self.form_frame, bg=Config.BACKGROUND_COLOR)
        form_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Image upload section
        image_section = tk.Frame(form_content, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        image_section.pack(fill="x", pady=(0, 20))
        
        image_header = tk.Label(
            image_section,
            text="Property Images",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        image_header.pack(pady=10)
        
        if self.property_data:
            # Show existing images for editing
            self.image_gallery = ImageGalleryWidget(
                image_section,
                self.property_data['id'],
                self.db_manager,
                bg=Config.CARD_COLOR
            )
            self.image_gallery.pack(fill="x", padx=20, pady=(0, 20))
        else:
            # Image upload widget for new property
            self.image_upload = ImageUploadWidget(
                image_section,
                on_image_selected=self.on_image_selected
            )
            self.image_upload.pack(padx=20, pady=(0, 20))
        
        # Form fields
        fields = [
            ("Title", "title", "text"),
            ("Description", "description", "text"),
            ("Property Type", "property_type", "combo"),
            ("Address", "address", "text"),
            ("City", "city", "text"),
            ("State", "state", "text"),
            ("ZIP Code", "zip_code", "text"),
            ("Price", "price", "number"),
            ("Bedrooms", "bedrooms", "number"),
            ("Bathrooms", "bathrooms", "number"),
            ("Square Feet", "square_feet", "number"),
            ("Lot Size (acres)", "lot_size", "number"),
            ("Year Built", "year_built", "number"),
            ("Listing Type", "listing_type", "combo"),
            ("Status", "status", "combo")
        ]
        
        self.field_vars = {}
        
        for label, field_name, field_type in fields:
            field_frame = tk.Frame(form_content, bg=Config.BACKGROUND_COLOR)
            field_frame.pack(fill="x", pady=(0, 15))
            
            tk.Label(
                field_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.BACKGROUND_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            if field_type == "combo":
                var = tk.StringVar()
                if field_name == "property_type":
                    values = ["House", "Apartment", "Condo", "Loft", "Townhouse"]
                elif field_name == "listing_type":
                    values = ["sale", "rent"]
                elif field_name == "status":
                    values = ["available", "sold", "rented", "pending"]
                
                combo = ttk.Combobox(field_frame, textvariable=var, values=values, state="readonly")
                combo.pack(fill="x")
                self.field_vars[field_name] = var
            else:
                entry = ModernEntry(field_frame, placeholder=f"Enter {label.lower()}")
                entry.pack(fill="x")
                self.field_vars[field_name] = entry
    
    def on_image_selected(self, filename):
        """Handle image selection for new property"""
        if filename:
            self.uploaded_images.append(filename)
    
    def populate_fields(self):
        """Populate fields with existing property data"""
        if not self.property_data:
            return
        
        for field_name, widget in self.field_vars.items():
            value = self.property_data.get(field_name, "")
            
            if isinstance(widget, tk.StringVar):
                widget.set(str(value))
            else:
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
    
    def save_property(self):
        """Save property data"""
        try:
            # Collect form data
            data = {}
            for field_name, widget in self.field_vars.items():
                if isinstance(widget, tk.StringVar):
                    data[field_name] = widget.get()
                else:
                    data[field_name] = widget.get_value()
            
            # Validate required fields
            required_fields = ['title', 'property_type', 'address', 'city', 'state', 'zip_code', 'price', 'listing_type']
            for field in required_fields:
                if not data.get(field):
                    messagebox.showerror("Error", f"Please fill in the {field.replace('_', ' ').title()} field")
                    return
            
            # Convert numeric fields
            numeric_fields = ['price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built']
            for field in numeric_fields:
                if data.get(field):
                    try:
                        data[field] = float(data[field]) if field in ['price', 'lot_size'] else int(data[field])
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid value for {field.replace('_', ' ').title()}")
                        return
                else:
                    data[field] = None
            
            # Save to database
            if self.property_data:
                # Update existing property
                success = self.db_manager.update_property(self.property_data['id'], data)
                message = "Property updated successfully"
            else:
                # Create new property
                success = self.db_manager.create_property(data)
                message = "Property created successfully"
                
                # Add uploaded images for new property
                if success and self.uploaded_images:
                    # Get the newly created property ID
                    cursor = self.db_manager.connection.cursor()
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    property_id = cursor.fetchone()[0]
                    cursor.close()
                    
                    # Add images to the property
                    for i, image_filename in enumerate(self.uploaded_images):
                        is_primary = (i == 0)  # First image is primary
                        self.db_manager.add_property_image(property_id, image_filename, is_primary)
            
            if success:
                messagebox.showinfo("Success", message)
                if self.on_success_callback:
                    self.on_success_callback()
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save property")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save property: {str(e)}")