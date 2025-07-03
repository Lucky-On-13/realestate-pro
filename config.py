# Application Configuration
import os

class Config:
    # Database - MySQL Configuration
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "real_estate_db"
    DB_USER = "root"
    DB_PASSWORD = ""  # Set your MySQL password here
    
    # Application Settings
    APP_NAME = "RealEstate Pro"
    VERSION = "1.0.0"
    
    # Window Settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # Colors
    PRIMARY_COLOR = "#2E86AB"
    SECONDARY_COLOR = "#A23B72"
    ACCENT_COLOR = "#F18F01"
    SUCCESS_COLOR = "#C73E1D"
    ERROR_COLOR = "#E74C3C"
    
    # Modern UI Colors
    BACKGROUND_COLOR = "#F8F9FA"
    CARD_COLOR = "#FFFFFF"
    TEXT_PRIMARY = "#2C3E50"
    TEXT_SECONDARY = "#7F8C8D"
    BORDER_COLOR = "#E1E8ED"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 16
    FONT_SIZE_MEDIUM = 12
    FONT_SIZE_SMALL = 10
    
    # Image Settings
    PROPERTY_IMAGE_SIZE = (300, 200)
    THUMBNAIL_SIZE = (150, 100)