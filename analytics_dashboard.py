import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import ModernButton
from config import Config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class AnalyticsDashboard:
    def __init__(self, parent, db_manager, admin_user):
        self.parent = parent
        self.db_manager = db_manager
        self.admin_user = admin_user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Analytics Dashboard")
        self.window.geometry("1400x900")
        self.window.configure(bg=Config.BACKGROUND_COLOR)
        
        self.create_widgets()
        self.load_analytics_data()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg=Config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=Config.PRIMARY_COLOR)
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        title_label = tk.Label(
            header_content,
            text="Analytics Dashboard",
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
        
        # Main content with notebook
        main_frame = tk.Frame(self.window, bg=Config.BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_overview_tab()
        self.create_sales_tab()
        self.create_properties_tab()
        self.create_users_tab()
    
    def create_overview_tab(self):
        """Create overview analytics tab"""
        overview_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(overview_frame, text="Overview")
        
        # Key metrics cards
        metrics_frame = tk.Frame(overview_frame, bg=Config.BACKGROUND_COLOR)
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        self.overview_cards = {}
        metrics_data = [
            ("Total Revenue", "total_revenue", Config.SUCCESS_COLOR),
            ("Properties Sold", "properties_sold", Config.PRIMARY_COLOR),
            ("Active Listings", "active_listings", Config.SECONDARY_COLOR),
            ("Avg. Sale Price", "avg_sale_price", Config.ACCENT_COLOR)
        ]
        
        for i, (title, key, color) in enumerate(metrics_data):
            card = self.create_metric_card(metrics_frame, title, "Loading...", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.overview_cards[key] = card
        
        # Configure grid weights
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)
        
        # Charts frame
        charts_frame = tk.Frame(overview_frame, bg=Config.BACKGROUND_COLOR)
        charts_frame.pack(fill="both", expand=True)
        
        # Revenue trend chart
        self.revenue_chart_frame = tk.Frame(charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.revenue_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        revenue_header = tk.Label(
            self.revenue_chart_frame,
            text="Revenue Trend (Last 12 Months)",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        revenue_header.pack(pady=10)
        
        # Property type distribution chart
        self.property_chart_frame = tk.Frame(charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.property_chart_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        property_header = tk.Label(
            self.property_chart_frame,
            text="Property Type Distribution",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        property_header.pack(pady=10)
    
    def create_sales_tab(self):
        """Create sales analytics tab"""
        sales_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(sales_frame, text="Sales Analytics")
        
        # Sales metrics
        sales_metrics_frame = tk.Frame(sales_frame, bg=Config.BACKGROUND_COLOR)
        sales_metrics_frame.pack(fill="x", pady=(0, 20))
        
        self.sales_cards = {}
        sales_data = [
            ("This Month Sales", "monthly_sales", Config.SUCCESS_COLOR),
            ("This Year Sales", "yearly_sales", Config.PRIMARY_COLOR),
            ("Avg. Days on Market", "avg_days_market", Config.SECONDARY_COLOR),
            ("Conversion Rate", "conversion_rate", Config.ACCENT_COLOR)
        ]
        
        for i, (title, key, color) in enumerate(sales_data):
            card = self.create_metric_card(sales_metrics_frame, title, "Loading...", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.sales_cards[key] = card
        
        # Configure grid weights
        for i in range(4):
            sales_metrics_frame.columnconfigure(i, weight=1)
        
        # Sales charts
        sales_charts_frame = tk.Frame(sales_frame, bg=Config.BACKGROUND_COLOR)
        sales_charts_frame.pack(fill="both", expand=True)
        
        # Monthly sales chart
        self.monthly_sales_frame = tk.Frame(sales_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.monthly_sales_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        monthly_header = tk.Label(
            self.monthly_sales_frame,
            text="Monthly Sales Volume",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        monthly_header.pack(pady=10)
        
        # Top performing properties
        top_properties_frame = tk.Frame(sales_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        top_properties_frame.pack(fill="both", expand=True)
        
        top_header = tk.Label(
            top_properties_frame,
            text="Top Performing Properties",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        top_header.pack(pady=10)
        
        # Top properties list
        self.top_properties_tree = ttk.Treeview(
            top_properties_frame,
            columns=("Property", "Type", "Sale Price", "Days on Market"),
            show="headings",
            height=8
        )
        
        for col in ["Property", "Type", "Sale Price", "Days on Market"]:
            self.top_properties_tree.heading(col, text=col)
            self.top_properties_tree.column(col, width=150)
        
        self.top_properties_tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_properties_tab(self):
        """Create properties analytics tab"""
        properties_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(properties_frame, text="Properties Analytics")
        
        # Property metrics
        prop_metrics_frame = tk.Frame(properties_frame, bg=Config.BACKGROUND_COLOR)
        prop_metrics_frame.pack(fill="x", pady=(0, 20))
        
        self.property_cards = {}
        property_data = [
            ("Total Properties", "total_properties", Config.PRIMARY_COLOR),
            ("Available", "available_properties", Config.SUCCESS_COLOR),
            ("Sold/Rented", "sold_properties", Config.SECONDARY_COLOR),
            ("Avg. Price", "avg_property_price", Config.ACCENT_COLOR)
        ]
        
        for i, (title, key, color) in enumerate(property_data):
            card = self.create_metric_card(prop_metrics_frame, title, "Loading...", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.property_cards[key] = card
        
        # Configure grid weights
        for i in range(4):
            prop_metrics_frame.columnconfigure(i, weight=1)
        
        # Property charts
        prop_charts_frame = tk.Frame(properties_frame, bg=Config.BACKGROUND_COLOR)
        prop_charts_frame.pack(fill="both", expand=True)
        
        # Price distribution chart
        self.price_dist_frame = tk.Frame(prop_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.price_dist_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        price_header = tk.Label(
            self.price_dist_frame,
            text="Price Distribution",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        price_header.pack(pady=10)
        
        # Location distribution chart
        self.location_dist_frame = tk.Frame(prop_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.location_dist_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        location_header = tk.Label(
            self.location_dist_frame,
            text="Properties by Location",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        location_header.pack(pady=10)
    
    def create_users_tab(self):
        """Create users analytics tab"""
        users_frame = tk.Frame(self.notebook, bg=Config.BACKGROUND_COLOR)
        self.notebook.add(users_frame, text="Users Analytics")
        
        # User metrics
        user_metrics_frame = tk.Frame(users_frame, bg=Config.BACKGROUND_COLOR)
        user_metrics_frame.pack(fill="x", pady=(0, 20))
        
        self.user_cards = {}
        user_data = [
            ("Total Users", "total_users", Config.PRIMARY_COLOR),
            ("Active Users", "active_users", Config.SUCCESS_COLOR),
            ("New This Month", "new_users_month", Config.SECONDARY_COLOR),
            ("User Growth", "user_growth", Config.ACCENT_COLOR)
        ]
        
        for i, (title, key, color) in enumerate(user_data):
            card = self.create_metric_card(user_metrics_frame, title, "Loading...", color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.user_cards[key] = card
        
        # Configure grid weights
        for i in range(4):
            user_metrics_frame.columnconfigure(i, weight=1)
        
        # User charts
        user_charts_frame = tk.Frame(users_frame, bg=Config.BACKGROUND_COLOR)
        user_charts_frame.pack(fill="both", expand=True)
        
        # User type distribution
        self.user_type_frame = tk.Frame(user_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.user_type_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        user_type_header = tk.Label(
            self.user_type_frame,
            text="User Type Distribution",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        user_type_header.pack(pady=10)
        
        # User registration trend
        self.user_trend_frame = tk.Frame(user_charts_frame, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        self.user_trend_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        user_trend_header = tk.Label(
            self.user_trend_frame,
            text="User Registration Trend",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        user_trend_header.pack(pady=10)
    
    def create_metric_card(self, parent, title, value, color):
        """Create a metric card"""
        card_frame = tk.Frame(parent, bg=Config.CARD_COLOR, relief="solid", borderwidth=1)
        
        # Header with color
        header_frame = tk.Frame(card_frame, bg=color, height=5)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Content
        content_frame = tk.Frame(card_frame, bg=Config.CARD_COLOR)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_SECONDARY
        )
        title_label.pack()
        
        value_label = tk.Label(
            content_frame,
            text=value,
            font=(Config.FONT_FAMILY, 18, "bold"),
            bg=Config.CARD_COLOR,
            fg=Config.TEXT_PRIMARY
        )
        value_label.pack(pady=(5, 0))
        
        # Store reference to value label for updates
        card_frame.value_label = value_label
        
        return card_frame
    
    def load_analytics_data(self):
        """Load all analytics data"""
        try:
            # Get analytics data from database
            analytics_data = self.db_manager.get_analytics_data()
            
            # Update overview cards
            self.overview_cards['total_revenue'].value_label.configure(
                text=f"${analytics_data['total_revenue']:,.0f}"
            )
            self.overview_cards['properties_sold'].value_label.configure(
                text=str(analytics_data['properties_sold'])
            )
            self.overview_cards['active_listings'].value_label.configure(
                text=str(analytics_data['active_listings'])
            )
            self.overview_cards['avg_sale_price'].value_label.configure(
                text=f"${analytics_data['avg_sale_price']:,.0f}"
            )
            
            # Update sales cards
            self.sales_cards['monthly_sales'].value_label.configure(
                text=f"${analytics_data['monthly_sales']:,.0f}"
            )
            self.sales_cards['yearly_sales'].value_label.configure(
                text=f"${analytics_data['yearly_sales']:,.0f}"
            )
            self.sales_cards['avg_days_market'].value_label.configure(
                text=f"{analytics_data['avg_days_market']} days"
            )
            self.sales_cards['conversion_rate'].value_label.configure(
                text=f"{analytics_data['conversion_rate']:.1f}%"
            )
            
            # Update property cards
            self.property_cards['total_properties'].value_label.configure(
                text=str(analytics_data['total_properties'])
            )
            self.property_cards['available_properties'].value_label.configure(
                text=str(analytics_data['available_properties'])
            )
            self.property_cards['sold_properties'].value_label.configure(
                text=str(analytics_data['sold_properties'])
            )
            self.property_cards['avg_property_price'].value_label.configure(
                text=f"${analytics_data['avg_property_price']:,.0f}"
            )
            
            # Update user cards
            self.user_cards['total_users'].value_label.configure(
                text=str(analytics_data['total_users'])
            )
            self.user_cards['active_users'].value_label.configure(
                text=str(analytics_data['active_users'])
            )
            self.user_cards['new_users_month'].value_label.configure(
                text=str(analytics_data['new_users_month'])
            )
            self.user_cards['user_growth'].value_label.configure(
                text=f"{analytics_data['user_growth']:+.1f}%"
            )
            
            # Load charts
            self.load_charts(analytics_data)
            
            # Load top properties
            self.load_top_properties()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load analytics data: {str(e)}")
    
    def load_charts(self, analytics_data):
        """Load chart data"""
        try:
            # This is a simplified version - in a real implementation,
            # you would create actual matplotlib charts here
            
            # For now, just show placeholder text
            placeholder_text = "Chart visualization would be displayed here\nwith matplotlib integration"
            
            # Revenue chart placeholder
            revenue_placeholder = tk.Label(
                self.revenue_chart_frame,
                text=placeholder_text,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                justify="center"
            )
            revenue_placeholder.pack(expand=True)
            
            # Property chart placeholder
            property_placeholder = tk.Label(
                self.property_chart_frame,
                text=placeholder_text,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_MEDIUM),
                bg=Config.CARD_COLOR,
                fg=Config.TEXT_SECONDARY,
                justify="center"
            )
            property_placeholder.pack(expand=True)
            
        except Exception as e:
            print(f"Error loading charts: {e}")
    
    def load_top_properties(self):
        """Load top performing properties"""
        try:
            top_properties = self.db_manager.get_top_properties()
            
            # Clear existing items
            for item in self.top_properties_tree.get_children():
                self.top_properties_tree.delete(item)
            
            # Add top properties
            for prop in top_properties[:10]:  # Top 10
                self.top_properties_tree.insert("", "end", values=(
                    prop['title'][:30] + "..." if len(prop['title']) > 30 else prop['title'],
                    prop['property_type'],
                    f"${prop['price']:,.0f}",
                    f"{prop.get('days_on_market', 'N/A')} days"
                ))
                
        except Exception as e:
            print(f"Error loading top properties: {e}")