import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton
from config import Config
from datetime import datetime

class TransactionManagementWindow:
    def __init__(self, parent, db_manager, admin_user):
        self.parent = parent
        self.db_manager = db_manager
        self.admin_user = admin_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Transaction Management")
        self.window.geometry("1400x800")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        self.selected_transaction = None
        
        self.create_widgets()
        self.load_transactions()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        title_label = tk.Label(
            header_content,
            text="Transaction Management",
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
        
        # Filter frame
        filter_frame = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_content = tk.Frame(filter_frame, bg=Config.CARD_COLOR)
        filter_content.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            filter_content,
            text="Filter by Status:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))
        
        self.status_filter = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            filter_content,
            textvariable=self.status_filter,
            values=["all", "pending", "completed", "cancelled"],
            state="readonly",
            width=15
        )
        status_combo.pack(side="left", padx=(0, 10))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_transactions())
        
        tk.Label(
            filter_content,
            text="Filter by Type:",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        ).pack(side="left", padx=(20, 10))
        
        self.type_filter = tk.StringVar(value="all")
        type_combo = ttk.Combobox(
            filter_content,
            textvariable=self.type_filter,
            values=["all", "purchase", "rent"],
            state="readonly",
            width=15
        )
        type_combo.pack(side="left", padx=(0, 10))
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.load_transactions())
        
        refresh_btn = ModernButton(
            filter_content,
            text="Refresh",
            command=self.load_transactions,
            style="outline",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            padx=10,
            pady=5
        )
        refresh_btn.pack(side="right")
        
        # Transactions list
        list_frame = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        list_frame.pack(fill="both", expand=True, padx=(0, 10))
        
        # Transactions treeview
        tree_frame = tk.Frame(list_frame, bg=Config.CARD_COLOR)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("ID", "Property", "Buyer", "Seller", "Type", "Amount", "Date", "Status"), 
            show="headings"
        )
        
        # Configure columns
        columns_config = [
            ("ID", 50),
            ("Property", 200),
            ("Buyer", 120),
            ("Seller", 120),
            ("Type", 80),
            ("Amount", 100),
            ("Date", 100),
            ("Status", 80)
        ]
        
        for col, width in columns_config:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_transaction_select)
        
        # Right panel - Transaction details and actions
        right_panel = tk.Frame(main_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1, width=350)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Details header
        details_header = tk.Label(
            right_panel,
            text="Transaction Details",
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
        
        self.complete_btn = ModernButton(
            actions_frame,
            text="Mark Complete",
            command=self.complete_transaction,
            style="success"
        )
        self.complete_btn.pack(fill="x", pady=(0, 10))
        
        self.cancel_btn = ModernButton(
            actions_frame,
            text="Cancel Transaction",
            command=self.cancel_transaction,
            style="outline"
        )
        self.cancel_btn.pack(fill="x", pady=(0, 10))
        
        self.delete_btn = ModernButton(
            actions_frame,
            text="Delete Transaction",
            command=self.delete_transaction,
            style="outline"
        )
        self.delete_btn.pack(fill="x")
        
        # Initially disable action buttons
        self.complete_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
    
    def load_transactions(self):
        """Load transactions into the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            status_filter = self.status_filter.get() if self.status_filter.get() != "all" else None
            type_filter = self.type_filter.get() if self.type_filter.get() != "all" else None
            
            transactions = self.db_manager.get_all_transactions_admin(status_filter, type_filter)
            
            for trans in transactions:
                # Format amount
                amount_text = f"${trans['amount']:,.0f}"
                
                # Format date
                date_text = trans['transaction_date'].strftime("%Y-%m-%d") if trans['transaction_date'] else "N/A"
                
                self.tree.insert("", "end", values=(
                    trans['id'],
                    trans['property_title'][:25] + "..." if len(trans['property_title']) > 25 else trans['property_title'],
                    trans['buyer_name'],
                    trans['seller_name'],
                    trans['transaction_type'].title(),
                    amount_text,
                    date_text,
                    trans['status'].title()
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")
    
    def on_transaction_select(self, event):
        """Handle transaction selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            transaction_id = item['values'][0]
            
            # Get full transaction details
            self.selected_transaction = self.db_manager.get_transaction_by_id_admin(transaction_id)
            
            if self.selected_transaction:
                self.display_transaction_details()
                self.update_action_buttons()
    
    def display_transaction_details(self):
        """Display selected transaction details"""
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_transaction:
            return
        
        trans = self.selected_transaction
        
        # Transaction details
        details = [
            ("ID", str(trans['id'])),
            ("Property", trans['property_title']),
            ("Property Address", trans['property_address']),
            ("Buyer", trans['buyer_name']),
            ("Buyer Email", trans['buyer_email']),
            ("Seller", trans['seller_name']),
            ("Seller Email", trans['seller_email']),
            ("Transaction Type", trans['transaction_type'].title()),
            ("Amount", f"${trans['amount']:,.0f}"),
            ("Date", trans['transaction_date'].strftime("%Y-%m-%d %H:%M") if trans['transaction_date'] else "N/A"),
            ("Status", trans['status'].title())
        ]
        
        for label, value in details:
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
            ).pack(side="top", anchor="w")
            
            tk.Label(
                detail_frame,
                text=value,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w",
                wraplength=300,
                justify="left"
            ).pack(side="top", anchor="w", padx=(10, 0))
        
        # Notes
        if trans.get('notes'):
            notes_frame = tk.Frame(self.details_frame, bg=Config.CARD_COLOR)
            notes_frame.pack(fill="x", pady=(10, 0))
            
            tk.Label(
                notes_frame,
                text="Notes:",
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold"),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x")
            
            tk.Label(
                notes_frame,
                text=trans['notes'],
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                anchor="w",
                wraplength=300,
                justify="left"
            ).pack(fill="x", pady=(5, 0), padx=(10, 0))
    
    def update_action_buttons(self):
        """Update action button states based on transaction status"""
        if not self.selected_transaction:
            self.complete_btn.configure(state="disabled")
            self.cancel_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            return
        
        status = self.selected_transaction['status']
        
        # Enable/disable buttons based on status
        if status == 'pending':
            self.complete_btn.configure(state="normal")
            self.cancel_btn.configure(state="normal")
        else:
            self.complete_btn.configure(state="disabled")
            self.cancel_btn.configure(state="disabled")
        
        # Delete is always available for admin
        self.delete_btn.configure(state="normal")
    
    def complete_transaction(self):
        """Mark transaction as completed"""
        if not self.selected_transaction or self.selected_transaction['status'] != 'pending':
            return
        
        result = messagebox.askyesno(
            "Confirm Completion",
            f"Are you sure you want to mark this transaction as completed?\n\n"
            f"Transaction ID: {self.selected_transaction['id']}\n"
            f"Property: {self.selected_transaction['property_title']}\n"
            f"Amount: ${self.selected_transaction['amount']:,.0f}"
        )
        
        if result:
            try:
                success = self.db_manager.update_transaction_status(
                    self.selected_transaction['id'], 
                    'completed'
                )
                if success:
                    messagebox.showinfo("Success", "Transaction marked as completed")
                    self.load_transactions()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", "Failed to update transaction status")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to complete transaction: {str(e)}")
    
    def cancel_transaction(self):
        """Cancel transaction"""
        if not self.selected_transaction or self.selected_transaction['status'] != 'pending':
            return
        
        result = messagebox.askyesno(
            "Confirm Cancellation",
            f"Are you sure you want to cancel this transaction?\n\n"
            f"Transaction ID: {self.selected_transaction['id']}\n"
            f"Property: {self.selected_transaction['property_title']}\n"
            f"Amount: ${self.selected_transaction['amount']:,.0f}\n\n"
            f"This will make the property available again."
        )
        
        if result:
            try:
                success = self.db_manager.cancel_transaction(self.selected_transaction['id'])
                if success:
                    messagebox.showinfo("Success", "Transaction cancelled successfully")
                    self.load_transactions()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", "Failed to cancel transaction")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel transaction: {str(e)}")
    
    def delete_transaction(self):
        """Delete transaction"""
        if not self.selected_transaction:
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this transaction?\n\n"
            f"Transaction ID: {self.selected_transaction['id']}\n"
            f"Property: {self.selected_transaction['property_title']}\n"
            f"Amount: ${self.selected_transaction['amount']:,.0f}\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            try:
                success = self.db_manager.delete_transaction(self.selected_transaction['id'])
                if success:
                    messagebox.showinfo("Success", "Transaction deleted successfully")
                    self.load_transactions()
                    self.clear_details()
                else:
                    messagebox.showerror("Error", "Failed to delete transaction")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")
    
    def clear_details(self):
        """Clear transaction details"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        self.selected_transaction = None
        self.complete_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")