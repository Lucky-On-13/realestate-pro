import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton, ModernEntry
from config import Config

class AuthWindow:
    def __init__(self, parent, db_manager, on_login_success=None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        
        self.window = tk.Toplevel(parent)
        self.window.title("Login / Sign Up")
        self.window.geometry("450x700")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.current_mode = "login"  # or "signup"
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title (fixed at top)
        self.title_label = tk.Label(
            main_container,
            text="Welcome Back!",
            font=(Config.FONT_FAMILY, 24, "bold"),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        self.title_label.pack(pady=(0, 20))
        
        # Scrollable content area
        self.create_scrollable_content(main_container)
        
        # Fixed buttons at bottom
        button_frame = tk.Frame(main_container, bg=Config.BACKGROUND_COLOR)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Action button
        self.action_btn = ModernButton(
            button_frame,
            text="Login",
            command=self.handle_action,
            style="primary"
        )
        self.action_btn.pack(fill="x", pady=(0, 15))
        
        # Switch mode button
        self.switch_btn = ModernButton(
            button_frame,
            text="Need an account? Sign up",
            command=self.switch_mode,
            style="outline"
        )
        self.switch_btn.pack(fill="x")
        
        # Set initial mode
        self.update_mode()
    
    def create_scrollable_content(self, parent):
        """Create scrollable content area for the form"""
        # Create canvas and scrollbar
        canvas_frame = tk.Frame(parent, bg=Config.BACKGROUND_COLOR)
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg=Config.BACKGROUND_COLOR, 
            highlightthickness=0,
            height=400  # Fixed height for scrollable area
        )
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        # Form frame inside canvas
        self.form_frame = tk.Frame(self.canvas, bg=Config.BACKGROUND_COLOR)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind events for scrolling
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Update canvas window width to match canvas width
            canvas_width = self.canvas.winfo_width()
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.form_frame.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mousewheel to canvas and all child widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.form_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Create form fields
        self.create_form_fields()
    
    def create_form_fields(self):
        """Create all form fields in the scrollable frame"""
        # Add padding to form frame
        form_content = tk.Frame(self.form_frame, bg=Config.BACKGROUND_COLOR)
        form_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Username
        username_label = tk.Label(
            form_content,
            text="Username:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 5))
        
        self.username_entry = ModernEntry(form_content, placeholder="Enter username")
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Email (for signup) - initially hidden
        self.email_label = tk.Label(
            form_content,
            text="Email:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        
        self.email_entry = ModernEntry(form_content, placeholder="Enter email")
        
        # Password
        password_label = tk.Label(
            form_content,
            text="Password:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ModernEntry(form_content, placeholder="Enter password", show="*")
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Name fields (for signup) - initially hidden
        self.first_name_label = tk.Label(
            form_content,
            text="First Name:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        
        self.first_name_entry = ModernEntry(form_content, placeholder="First name")
        
        self.last_name_label = tk.Label(
            form_content,
            text="Last Name:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        
        self.last_name_entry = ModernEntry(form_content, placeholder="Last name")
        
        # Phone (for signup) - initially hidden
        self.phone_label = tk.Label(
            form_content,
            text="Phone (Optional):",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.BACKGROUND_COLOR,
            fg=Config.TEXT_PRIMARY,
            anchor="w"
        )
        
        self.phone_entry = ModernEntry(form_content, placeholder="Enter phone number")
        
        # Bind mousewheel to all form elements
        self.bind_mousewheel_to_children(form_content)
    
    def bind_mousewheel_to_children(self, widget):
        """Recursively bind mousewheel event to all children"""
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        widget.bind("<MouseWheel>", on_mousewheel)
        for child in widget.winfo_children():
            self.bind_mousewheel_to_children(child)
    
    def update_mode(self):
        """Update UI based on current mode"""
        if self.current_mode == "login":
            self.title_label.configure(text="Welcome Back!")
            self.action_btn.configure(text="Login")
            self.switch_btn.configure(text="Need an account? Sign up")
            
            # Hide signup fields
            self.hide_signup_fields()
            
        else:  # signup
            self.title_label.configure(text="Create Account")
            self.action_btn.configure(text="Sign Up")
            self.switch_btn.configure(text="Already have an account? Login")
            
            # Show signup fields
            self.show_signup_fields()
        
        # Update scroll region after mode change
        self.window.after(100, self.update_scroll_region)
    
    def hide_signup_fields(self):
        """Hide signup-specific fields"""
        self.email_label.pack_forget()
        self.email_entry.pack_forget()
        self.first_name_label.pack_forget()
        self.first_name_entry.pack_forget()
        self.last_name_label.pack_forget()
        self.last_name_entry.pack_forget()
        self.phone_label.pack_forget()
        self.phone_entry.pack_forget()
    
    def show_signup_fields(self):
        """Show signup-specific fields"""
        # Insert email field after username
        self.email_label.pack(fill="x", pady=(0, 5), after=self.username_entry)
        self.email_entry.pack(fill="x", pady=(0, 15), after=self.email_label)
        
        # Insert name fields after password
        self.first_name_label.pack(fill="x", pady=(0, 5), after=self.password_entry)
        self.first_name_entry.pack(fill="x", pady=(0, 15), after=self.first_name_label)
        
        self.last_name_label.pack(fill="x", pady=(0, 5), after=self.first_name_entry)
        self.last_name_entry.pack(fill="x", pady=(0, 15), after=self.last_name_label)
        
        # Insert phone field at the end
        self.phone_label.pack(fill="x", pady=(0, 5), after=self.last_name_entry)
        self.phone_entry.pack(fill="x", pady=(0, 15), after=self.phone_label)
        
        # Bind mousewheel to new elements
        self.bind_mousewheel_to_children(self.email_label)
        self.bind_mousewheel_to_children(self.email_entry)
        self.bind_mousewheel_to_children(self.first_name_label)
        self.bind_mousewheel_to_children(self.first_name_entry)
        self.bind_mousewheel_to_children(self.last_name_label)
        self.bind_mousewheel_to_children(self.last_name_entry)
        self.bind_mousewheel_to_children(self.phone_label)
        self.bind_mousewheel_to_children(self.phone_entry)
    
    def update_scroll_region(self):
        """Update the scroll region"""
        self.form_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def switch_mode(self):
        """Switch between login and signup modes"""
        self.current_mode = "signup" if self.current_mode == "login" else "login"
        self.update_mode()
        
        # Clear all fields
        self.clear_all_fields()
    
    def clear_all_fields(self):
        """Clear all input fields"""
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        
        # Reset placeholders
        if self.username_entry.placeholder:
            self.username_entry.put_placeholder()
        if self.email_entry.placeholder:
            self.email_entry.put_placeholder()
        if self.password_entry.placeholder:
            self.password_entry.put_placeholder()
        if self.first_name_entry.placeholder:
            self.first_name_entry.put_placeholder()
        if self.last_name_entry.placeholder:
            self.last_name_entry.put_placeholder()
        if self.phone_entry.placeholder:
            self.phone_entry.put_placeholder()
    
    def handle_action(self):
        """Handle login or signup action"""
        if self.current_mode == "login":
            self.handle_login()
        else:
            self.handle_signup()
    
    def handle_login(self):
        """Handle user login"""
        username = self.username_entry.get_value()
        password = self.password_entry.get_value()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        user = self.db_manager.authenticate_user(username, password)
        if user:
            messagebox.showinfo("Success", f"Welcome back, {user['first_name']}!")
            if self.on_login_success:
                self.on_login_success(user)
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def handle_signup(self):
        """Handle user signup"""
        username = self.username_entry.get_value()
        email = self.email_entry.get_value()
        password = self.password_entry.get_value()
        first_name = self.first_name_entry.get_value()
        last_name = self.last_name_entry.get_value()
        phone = self.phone_entry.get_value()
        
        if not all([username, email, password, first_name, last_name]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        success = self.db_manager.create_user(
            username, email, password, first_name, last_name, phone
        )
        
        if success:
            messagebox.showinfo("Success", "Account created successfully! You can now log in.")
            self.current_mode = "login"
            self.update_mode()
            self.clear_all_fields()
        else:
            messagebox.showerror("Error", "Username or email already exists")