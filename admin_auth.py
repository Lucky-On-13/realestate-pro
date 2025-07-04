import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, ModernEntry
from config import Config

class AdminAuthWindow:
    def __init__(self, parent, db_manager, on_login_success=None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        
        self.window = tk.Toplevel(parent)
        self.window.title("Admin Login")
        self.window.geometry("400x300")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Admin Access",
            font=(Config.FONT_FAMILY, 20, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        title_label.pack(pady=(0, 30))
        
        # Username
        username_label = tk.Label(
            main_container,
            text="Admin Username:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 5))
        
        self.username_entry = ModernEntry(main_container, placeholder="Enter admin username")
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        password_label = tk.Label(
            main_container,
            text="Admin Password:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ModernEntry(main_container, placeholder="Enter admin password", show="*")
        self.password_entry.pack(fill="x", pady=(0, 25))
        
        # Login button
        login_btn = ModernButton(
            main_container,
            text="Login as Admin",
            command=self.handle_login,
            style="primary"
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        # Cancel button
        cancel_btn = ModernButton(
            main_container,
            text="Cancel",
            command=self.window.destroy,
            style="outline"
        )
        cancel_btn.pack(fill="x")
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.handle_login())
    
    def handle_login(self):
        """Handle admin login"""
        username = self.username_entry.get_value()
        password = self.password_entry.get_value()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Check admin credentials
        admin = self.db_manager.authenticate_admin(username, password)
        if admin:
            messagebox.showinfo("Success", f"Welcome, {admin['first_name']}!")
            if self.on_login_success:
                self.on_login_success(admin)
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Invalid admin credentials")