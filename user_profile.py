import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, ModernEntry
from config import Config
from favorites_window import FavoritesWindow

class UserProfileWindow:
    def __init__(self, parent, db_manager, current_user, on_user_updated=None):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.on_user_updated = on_user_updated
        
        self.window = tk.Toplevel(parent)
        self.window.title("My Profile")
        self.window.geometry("600x700")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_user_data()
    
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
            text="My Profile",
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
        
        # Main content
        main_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # User info section
        self.create_user_info_section(main_frame)
        
        # Statistics section
        self.create_statistics_section(main_frame)
        
        # Actions section
        self.create_actions_section(main_frame)
        
        # Profile edit section
        self.create_edit_section(main_frame)
    
    def create_user_info_section(self, parent):
        """Create user information display section"""
        info_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = tk.Frame(info_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        info_content.pack(fill="both", expand=True)
        
        # Section header
        header_label = tk.Label(
            info_content,
            text="Account Information",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        header_label.pack(fill="x", pady=(0, 15))
        
        # User details
        self.info_labels = {}
        user_details = [
            ("Username", self.current_user['username']),
            ("Email", self.current_user['email']),
            ("Full Name", f"{self.current_user['first_name']} {self.current_user['last_name']}"),
            ("Phone", self.current_user.get('phone', 'Not provided')),
            ("Account Type", self.current_user['user_type'].title())
        ]
        
        for label, value in user_details:
            detail_frame = tk.Frame(info_content, bg=Config.CARD_COLOR)
            detail_frame.pack(fill="x", pady=5)
            
            tk.Label(
                detail_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                width=15,
                anchor="w"
            ).pack(side="left")
            
            value_label = tk.Label(
                detail_frame,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w"
            )
            value_label.pack(side="left", padx=(10, 0))
            
            self.info_labels[label.lower().replace(' ', '_')] = value_label
    
    def create_statistics_section(self, parent):
        """Create user statistics section"""
        stats_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_content = tk.Frame(stats_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        stats_content.pack(fill="both", expand=True)
        
        # Section header
        header_label = tk.Label(
            stats_content,
            text="Activity Statistics",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        header_label.pack(fill="x", pady=(0, 15))
        
        # Statistics grid
        stats_grid = tk.Frame(stats_content, bg=Config.CARD_COLOR)
        stats_grid.pack(fill="x")
        
        # Load and display statistics
        try:
            stats = self.db_manager.get_user_statistics(self.current_user['id'])
            
            stat_items = [
                ("Properties Owned", stats.get('properties_owned', 0), Config.PRIMARY_COLOR),
                ("Transactions", stats.get('transactions', 0), Config.SECONDARY_COLOR),
                ("Favorite Properties", stats.get('favorites', 0), Config.ACCENT_COLOR)
            ]
            
            for i, (label, value, color) in enumerate(stat_items):
                stat_card = self.create_stat_card(stats_grid, label, str(value), color)
                stat_card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
            # Configure grid weights
            for i in range(3):
                stats_grid.columnconfigure(i, weight=1)
                
        except Exception as e:
            print(f"Error loading user statistics: {e}")
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=Config.BACKGROUND_COLOR, relief="solid", borderwidth=1)
        
        # Header with color
        header_frame = tk.Frame(card_frame, bg=color, height=5)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Content
        content_frame = tk.Frame(card_frame, bg=Config.BACKGROUND_COLOR)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        value_label = tk.Label(
            content_frame,
            text=value,
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        value_label.pack()
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_SECONDARY
        )
        title_label.pack(pady=(5, 0))
        
        return card_frame
    
    def create_actions_section(self, parent):
        """Create quick actions section"""
        actions_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions_content = tk.Frame(actions_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        actions_content.pack(fill="both", expand=True)
        
        # Section header
        header_label = tk.Label(
            actions_content,
            text="Quick Actions",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        header_label.pack(fill="x", pady=(0, 15))
        
        # Action buttons
        buttons_frame = tk.Frame(actions_content, bg=Config.CARD_COLOR)
        buttons_frame.pack(fill="x")
        
        favorites_btn = ModernButton(
            buttons_frame,
            text="View My Favorites",
            command=self.open_favorites,
            style="primary"
        )
        favorites_btn.pack(side="left", padx=(0, 10))
        
        transactions_btn = ModernButton(
            buttons_frame,
            text="My Transactions",
            command=self.view_transactions,
            style="secondary"
        )
        transactions_btn.pack(side="left")
    
    def create_edit_section(self, parent):
        """Create profile edit section"""
        edit_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        edit_frame.pack(fill="both", expand=True)
        
        edit_content = tk.Frame(edit_frame, bg=Config.CARD_COLOR, padx=20, pady=20)
        edit_content.pack(fill="both", expand=True)
        
        # Section header
        header_label = tk.Label(
            edit_content,
            text="Edit Profile",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        header_label.pack(fill="x", pady=(0, 15))
        
        # Edit form
        self.field_vars = {}
        
        fields = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Phone", "phone"),
            ("New Password", "password")
        ]
        
        for label, field_name in fields:
            field_frame = tk.Frame(edit_content, bg=Config.CARD_COLOR)
            field_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(
                field_frame,
                text=f"{label}:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            if field_name == "password":
                entry = ModernEntry(field_frame, placeholder="Leave blank to keep current password", show="*")
            else:
                entry = ModernEntry(field_frame, placeholder=f"Enter {label.lower()}")
            
            entry.pack(fill="x")
            self.field_vars[field_name] = entry
        
        # Update button
        update_btn = ModernButton(
            edit_content,
            text="Update Profile",
            command=self.update_profile,
            style="success"
        )
        update_btn.pack(pady=(20, 0))
    
    def load_user_data(self):
        """Load current user data into edit fields"""
        self.field_vars['first_name'].delete(0, tk.END)
        self.field_vars['first_name'].insert(0, self.current_user['first_name'])
        
        self.field_vars['last_name'].delete(0, tk.END)
        self.field_vars['last_name'].insert(0, self.current_user['last_name'])
        
        if self.current_user.get('phone'):
            self.field_vars['phone'].delete(0, tk.END)
            self.field_vars['phone'].insert(0, self.current_user['phone'])
    
    def update_profile(self):
        """Update user profile"""
        try:
            # Collect form data
            data = {
                'username': self.current_user['username'],  # Keep existing username
                'email': self.current_user['email'],  # Keep existing email
                'first_name': self.field_vars['first_name'].get_value(),
                'last_name': self.field_vars['last_name'].get_value(),
                'phone': self.field_vars['phone'].get_value(),
                'user_type': self.current_user['user_type'],  # Keep existing type
                'password': self.field_vars['password'].get_value()
            }
            
            # Validate required fields
            if not data['first_name'] or not data['last_name']:
                messagebox.showerror("Error", "First name and last name are required")
                return
            
            # Validate password length if provided
            if data['password'] and len(data['password']) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
            
            # Update in database
            success = self.db_manager.update_user_admin(self.current_user['id'], data)
            
            if success:
                messagebox.showinfo("Success", "Profile updated successfully")
                
                # Update current user data
                self.current_user['first_name'] = data['first_name']
                self.current_user['last_name'] = data['last_name']
                self.current_user['phone'] = data['phone']
                
                # Update display
                self.info_labels['full_name'].configure(text=f"{data['first_name']} {data['last_name']}")
                self.info_labels['phone'].configure(text=data['phone'] or 'Not provided')
                
                # Clear password field
                self.field_vars['password'].delete(0, tk.END)
                if self.field_vars['password'].placeholder:
                    self.field_vars['password'].put_placeholder()
                
                # Notify parent if callback provided
                if self.on_user_updated:
                    self.on_user_updated(self.current_user)
                    
            else:
                messagebox.showerror("Error", "Failed to update profile")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update profile: {str(e)}")
    
    def open_favorites(self):
        """Open favorites window"""
        FavoritesWindow(self.window, self.db_manager, self.current_user)
    
    def view_transactions(self):
        """View user transactions"""
        try:
            # Get user transactions
            transactions = self.db_manager.get_all_transactions_admin()
            user_transactions = [t for t in transactions if t['buyer_id'] == self.current_user['id'] or t['seller_id'] == self.current_user['id']]
            
            if not user_transactions:
                messagebox.showinfo("No Transactions", "You don't have any transactions yet.")
                return
            
            # Create transactions display window
            self.show_transactions_window(user_transactions)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")
    
    def show_transactions_window(self, transactions):
        """Show user transactions in a new window"""
        trans_window = tk.Toplevel(self.window)
        trans_window.title("My Transactions")
        trans_window.geometry("800x600")
        trans_window.configure(bg=Config.BACKGROUND_COLOR)
        trans_window.transient(self.window)
        
        # Header
        header_frame = tk.Frame(trans_window, bg=Config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="My Transactions",
            font=(Config.FONT_FAMILY, 16, "bold"),
            bg=Config.PRIMARY_COLOR,
            fg="white"
        ).pack(pady=15)
        
        # Transactions list
        list_frame = tk.Frame(trans_window, bg=Config.BACKGROUND_COLOR)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview
        tree = ttk.Treeview(
            list_frame,
            columns=("Property", "Type", "Amount", "Date", "Status"),
            show="headings"
        )
        
        # Configure columns
        tree.heading("Property", text="Property")
        tree.heading("Type", text="Type")
        tree.heading("Amount", text="Amount")
        tree.heading("Date", text="Date")
        tree.heading("Status", text="Status")
        
        tree.column("Property", width=200)
        tree.column("Type", width=100)
        tree.column("Amount", width=120)
        tree.column("Date", width=120)
        tree.column("Status", width=100)
        
        # Add transactions
        for trans in transactions:
            tree.insert("", "end", values=(
                trans['property_title'][:30] + "..." if len(trans['property_title']) > 30 else trans['property_title'],
                trans['transaction_type'].title(),
                f"${trans['amount']:,.0f}",
                trans['transaction_date'].strftime("%Y-%m-%d") if trans['transaction_date'] else "N/A",
                trans['status'].title()
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = ModernButton(
            trans_window,
            text="Close",
            command=trans_window.destroy,
            style="outline"
        )
        close_btn.pack(pady=10)