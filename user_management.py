import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, ModernEntry
from config import Config

class UserManagementWindow:
    def __init__(self, parent, db_manager, admin_user):
        self.parent = parent
        self.db_manager = db_manager
        self.admin_user = admin_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("User Management")
        self.window.geometry("1200x800")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        self.selected_user = None
        
        self.create_widgets()
        self.load_users()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        title_label = tk.Label(
            header_content,
            text="User Management",
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
        
        # Left panel - User list
        left_panel = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # User list header
        list_header = tk.Frame(left_panel, bg=Config.CARD_COLOR)
        list_header.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            list_header,
            text="Users",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        ).pack(side="left")
        
        refresh_btn = ModernButton(
            list_header,
            text="Refresh",
            command=self.load_users,
            style="outline",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            padx=10,
            pady=5
        )
        refresh_btn.pack(side="right")
        
        # Users treeview
        tree_frame = tk.Frame(left_panel, bg=Config.CARD_COLOR)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Name", "Email", "Type", "Status"), show="headings")
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50)
        self.tree.column("Username", width=120)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Type", width=80)
        self.tree.column("Status", width=80)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        # Right panel - User details and actions
        right_panel = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1, width=400)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Details header
        details_header = tk.Label(
            right_panel,
            text="User Details",
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
            text="Edit User",
            command=self.edit_user,
            style="primary"
        )
        self.edit_btn.pack(fill="x", pady=(0, 10))
        
        self.toggle_status_btn = ModernButton(
            actions_frame,
            text="Toggle Status",
            command=self.toggle_user_status,
            style="accent"
        )
        self.toggle_status_btn.pack(fill="x", pady=(0, 10))
        
        self.delete_btn = ModernButton(
            actions_frame,
            text="Delete User",
            command=self.delete_user,
            style="outline"
        )
        self.delete_btn.pack(fill="x", pady=(0, 10))
        
        self.add_btn = ModernButton(
            actions_frame,
            text="Add New User",
            command=self.add_user,
            style="success"
        )
        self.add_btn.pack(fill="x")
        
        # Initially disable action buttons
        self.edit_btn.configure(state="disabled")
        self.toggle_status_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
    
    def load_users(self):
        """Load all users into the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            users = self.db_manager.get_all_users_admin()
            
            for user in users:
                full_name = f"{user['first_name']} {user['last_name']}"
                status = "Active" if user['is_active'] else "Inactive"
                
                self.tree.insert("", "end", values=(
                    user['id'],
                    user['username'],
                    full_name,
                    user['email'],
                    user['user_type'].title(),
                    status
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
    
    def on_user_select(self, event):
        """Handle user selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            user_id = item['values'][0]
            
            # Get full user details
            self.selected_user = self.db_manager.get_user_by_id_admin(user_id)
            
            if self.selected_user:
                self.display_user_details()
                self.edit_btn.configure(state="normal")
                self.toggle_status_btn.configure(state="normal")
                self.delete_btn.configure(state="normal")
                
                # Update toggle button text
                status_text = "Deactivate" if self.selected_user['is_active'] else "Activate"
                self.toggle_status_btn.configure(text=f"{status_text} User")
    
    def display_user_details(self):
        """Display selected user details"""
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_user:
            return
        
        user = self.selected_user
        
        # User details
        details = [
            ("ID", str(user['id'])),
            ("Username", user['username']),
            ("Email", user['email']),
            ("First Name", user['first_name']),
            ("Last Name", user['last_name']),
            ("Phone", user.get('phone', 'N/A')),
            ("User Type", user['user_type'].title()),
            ("Status", "Active" if user['is_active'] else "Inactive"),
            ("Created", user['created_at'].strftime("%Y-%m-%d %H:%M") if user.get('created_at') else 'N/A')
        ]
        
        for label, value in details:
            detail_frame = tk.Frame(self.details_frame, bg=Config.CARD_COLOR)
            detail_frame.pack(fill="x", pady=3)
            
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
        
        # User statistics
        try:
            stats = self.db_manager.get_user_statistics(user['id'])
            
            stats_frame = tk.Frame(self.details_frame, bg=Config.CARD_COLOR)
            stats_frame.pack(fill="x", pady=(15, 0))
            
            tk.Label(
                stats_frame,
                text="Statistics:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x")
            
            stat_details = [
                ("Properties Owned", str(stats.get('properties_owned', 0))),
                ("Transactions", str(stats.get('transactions', 0))),
                ("Favorites", str(stats.get('favorites', 0)))
            ]
            
            for label, value in stat_details:
                stat_frame = tk.Frame(stats_frame, bg=Config.CARD_COLOR)
                stat_frame.pack(fill="x", pady=2)
                
                tk.Label(
                    stat_frame,
                    text=f"  {label}:",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                    bg=Config.CARD_COLOR,
                    fg=Config.TEXT_PRIMARY,
                    width=15,
                    anchor="w"
                ).pack(side="left")
                
                tk.Label(
                    stat_frame,
                    text=value,
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                    bg=Config.CARD_COLOR,
                    fg=Config.TEXT_SECONDARY,
                    anchor="w"
                ).pack(side="left")
                
        except Exception as e:
            print(f"Error loading user statistics: {e}")
    
    def edit_user(self):
        """Open user edit dialog"""
        if not self.selected_user:
            return
        
        UserEditDialog(self.window, self.db_manager, self.selected_user, self.on_user_updated)
    
    def toggle_user_status(self):
        """Toggle user active status"""
        if not self.selected_user:
            return
        
        current_status = self.selected_user['is_active']
        new_status = not current_status
        action = "activate" if new_status else "deactivate"
        
        result = messagebox.askyesno(
            "Confirm Status Change",
            f"Are you sure you want to {action} user '{self.selected_user['username']}'?"
        )
        
        if result:
            try:
                success = self.db_manager.update_user_status(self.selected_user['id'], new_status)
                if success:
                    messagebox.showinfo("Success", f"User {action}d successfully")
                    self.load_users()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", f"Failed to {action} user")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to {action} user: {str(e)}")
    
    def delete_user(self):
        """Delete selected user"""
        if not self.selected_user:
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{self.selected_user['username']}'?\n\n"
            f"This will also delete all associated data including:\n"
            f"- User's properties\n"
            f"- User's transactions\n"
            f"- User's favorites\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            try:
                success = self.db_manager.delete_user(self.selected_user['id'])
                if success:
                    messagebox.showinfo("Success", "User deleted successfully")
                    self.load_users()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", "Failed to delete user")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def add_user(self):
        """Open add user dialog"""
        UserEditDialog(self.window, self.db_manager, None, self.on_user_updated)
    
    def on_user_updated(self):
        """Callback when user is updated/added"""
        self.load_users()
        self.clear_details()
    
    def clear_details(self):
        """Clear user details"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        self.selected_user = None
        self.edit_btn.configure(state="disabled")
        self.toggle_status_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")

class UserEditDialog:
    def __init__(self, parent, db_manager, user_data, on_success_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.on_success_callback = on_success_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit User" if user_data else "Add User")
        self.window.geometry("500x600")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        if user_data:
            self.populate_fields()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_text = "Edit User" if self.user_data else "Add New User"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=(Config.FONT_FAMILY, 14, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=10)
        
        # Form
        form_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Form fields
        fields = [
            ("Username", "username", "text"),
            ("Email", "email", "text"),
            ("First Name", "first_name", "text"),
            ("Last Name", "last_name", "text"),
            ("Phone", "phone", "text"),
            ("User Type", "user_type", "combo"),
            ("Password", "password", "password")
        ]
        
        self.field_vars = {}
        
        for label, field_name, field_type in fields:
            field_frame = tk.Frame(form_frame, bg=Config.BACKGROUND_COLOR)
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
                values = ["buyer", "seller", "agent"]
                combo = ttk.Combobox(field_frame, textvariable=var, values=values, state="readonly")
                combo.pack(fill="x")
                self.field_vars[field_name] = var
            elif field_type == "password":
                entry = ModernEntry(field_frame, placeholder=f"Enter {label.lower()}", show="*")
                entry.pack(fill="x")
                self.field_vars[field_name] = entry
                
                # Add note for edit mode
                if self.user_data:
                    note_label = tk.Label(
                        field_frame,
                        text="Leave blank to keep current password",
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                        bg=Config.BACKGROUND_COLOR,
                        fg=Config.TEXT_SECONDARY
                    )
                    note_label.pack(fill="x", pady=(2, 0))
            else:
                entry = ModernEntry(field_frame, placeholder=f"Enter {label.lower()}")
                entry.pack(fill="x")
                self.field_vars[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=Config.BACKGROUND_COLOR)
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ModernButton(
            button_frame,
            text="Save User",
            command=self.save_user,
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
    
    def populate_fields(self):
        """Populate fields with existing user data"""
        if not self.user_data:
            return
        
        for field_name, widget in self.field_vars.items():
            if field_name == "password":
                continue  # Don't populate password field
            
            value = self.user_data.get(field_name, "")
            
            if isinstance(widget, tk.StringVar):
                widget.set(str(value))
            else:
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
    
    def save_user(self):
        """Save user data"""
        try:
            # Collect form data
            data = {}
            for field_name, widget in self.field_vars.items():
                if isinstance(widget, tk.StringVar):
                    data[field_name] = widget.get()
                else:
                    data[field_name] = widget.get_value()
            
            # Validate required fields
            required_fields = ['username', 'email', 'first_name', 'last_name', 'user_type']
            if not self.user_data:  # New user needs password
                required_fields.append('password')
            
            for field in required_fields:
                if not data.get(field):
                    messagebox.showerror("Error", f"Please fill in the {field.replace('_', ' ').title()} field")
                    return
            
            # Validate email format
            email = data['email']
            if '@' not in email or '.' not in email:
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            # Validate password length for new users
            if not self.user_data and len(data['password']) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
            
            # Save to database
            if self.user_data:
                # Update existing user
                success = self.db_manager.update_user_admin(self.user_data['id'], data)
                message = "User updated successfully"
            else:
                # Create new user
                success = self.db_manager.create_user_admin(data)
                message = "User created successfully"
            
            if success:
                messagebox.showinfo("Success", message)
                if self.on_success_callback:
                    self.on_success_callback()
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save user. Username or email may already exist.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")