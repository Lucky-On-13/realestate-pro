import mysql.connector
from mysql.connector import Error
import hashlib
import datetime
from typing import List, Dict, Optional, Tuple
from config import Config

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect_to_database()
        self.init_database()
    
    def connect_to_database(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                autocommit=True
            )
            
            if self.connection.is_connected():
                print("Connected to MySQL server")
                
                # Create database if it doesn't exist
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
                cursor.execute(f"USE {Config.DB_NAME}")
                cursor.close()
                
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def init_database(self):
        """Initialize the database with required tables"""
        if not self.connection or not self.connection.is_connected():
            self.connect_to_database()
        
        try:
            cursor = self.connection.cursor()
            
            # Drop existing tables to recreate with proper structure
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("DROP TABLE IF EXISTS favorites")
            cursor.execute("DROP TABLE IF EXISTS transactions")
            cursor.execute("DROP TABLE IF EXISTS property_images")
            cursor.execute("DROP TABLE IF EXISTS properties")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # Users table
            cursor.execute('''
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    user_type ENUM('buyer', 'seller', 'agent') DEFAULT 'buyer',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Properties table
            cursor.execute('''
                CREATE TABLE properties (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    property_type ENUM('House', 'Apartment', 'Condo', 'Loft', 'Townhouse') NOT NULL,
                    address VARCHAR(200) NOT NULL,
                    city VARCHAR(100) NOT NULL,
                    state VARCHAR(50) NOT NULL,
                    zip_code VARCHAR(10) NOT NULL,
                    price DECIMAL(12,2) NOT NULL,
                    bedrooms INT,
                    bathrooms INT,
                    square_feet INT,
                    lot_size DECIMAL(8,2),
                    year_built INT,
                    listing_type ENUM('sale', 'rent') NOT NULL,
                    owner_id INT,
                    agent_id INT,
                    status ENUM('available', 'sold', 'rented', 'pending') DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(id),
                    FOREIGN KEY (agent_id) REFERENCES users(id)
                )
            ''')
            
            # Property images table
            cursor.execute('''
                CREATE TABLE property_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    property_id INT,
                    image_path VARCHAR(500) NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    property_id INT,
                    buyer_id INT,
                    seller_id INT,
                    transaction_type ENUM('purchase', 'rent') NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
                    notes TEXT,
                    FOREIGN KEY (property_id) REFERENCES properties(id),
                    FOREIGN KEY (buyer_id) REFERENCES users(id),
                    FOREIGN KEY (seller_id) REFERENCES users(id)
                )
            ''')
            
            # Favorites table
            cursor.execute('''
                CREATE TABLE favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    property_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_favorite (user_id, property_id)
                )
            ''')
            
            cursor.close()
            print("Database tables created successfully")
            self.populate_sample_data()
            
        except Error as e:
            print(f"Error initializing database: {e}")
            raise
    
    def populate_sample_data(self):
        """Populate database with sample data"""
        try:
            cursor = self.connection.cursor()
            
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) FROM properties")
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.close()
                return
            
            # Create a default agent user first
            default_agent = {
                'username': 'agent_demo',
                'email': 'agent@realestate.com',
                'password': 'demo123',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '555-0123',
                'user_type': 'agent'
            }
            
            password_hash = self.hash_password(default_agent['password'])
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, 
                                        last_name, phone, user_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (default_agent['username'], default_agent['email'], password_hash,
                  default_agent['first_name'], default_agent['last_name'], 
                  default_agent['phone'], default_agent['user_type']))
            
            # Get the agent ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (default_agent['username'],))
            agent_id = cursor.fetchone()[0]
            
            # Sample properties
            sample_properties = [
                ("Luxury Downtown Condo", "Modern 2-bedroom condo in the heart of downtown", "Condo", 
                 "123 Main St", "New York", "NY", "10001", 750000, 2, 2, 1200, 0, 2020, "sale", agent_id, agent_id),
                ("Cozy Suburban Home", "Beautiful 3-bedroom family home with garden", "House", 
                 "456 Oak Ave", "San Francisco", "CA", "94102", 1200000, 3, 2, 1800, 0.25, 2015, "sale", agent_id, agent_id),
                ("Modern Apartment", "Spacious 1-bedroom apartment with city views", "Apartment", 
                 "789 Pine St", "Seattle", "WA", "98101", 2500, 1, 1, 900, 0, 2018, "rent", agent_id, agent_id),
                ("Family Ranch", "Large 4-bedroom ranch style home", "House", 
                 "321 Elm Dr", "Austin", "TX", "78701", 650000, 4, 3, 2400, 0.5, 2010, "sale", agent_id, agent_id),
                ("Studio Loft", "Trendy studio loft in arts district", "Loft", 
                 "654 Arts Blvd", "Portland", "OR", "97201", 1800, 1, 1, 750, 0, 2019, "rent", agent_id, agent_id)
            ]
            
            cursor.executemany('''
                INSERT INTO properties (title, description, property_type, address, city, state, 
                                      zip_code, price, bedrooms, bathrooms, square_feet, lot_size, 
                                      year_built, listing_type, owner_id, agent_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', sample_properties)
            
            cursor.close()
            print("Sample data populated successfully")
            
        except Error as e:
            print(f"Error populating sample data: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str, last_name: str, phone: str = None, 
                   user_type: str = 'buyer') -> bool:
        """Create a new user"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, 
                                 last_name, phone, user_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (username, email, password_hash, first_name, last_name, phone, user_type))
            
            cursor.close()
            return True
            
        except mysql.connector.IntegrityError:
            return False
        except Error as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, first_name, last_name, phone, user_type
                FROM users WHERE username = %s AND password_hash = %s AND is_active = TRUE
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'first_name': result[3],
                    'last_name': result[4],
                    'phone': result[5],
                    'user_type': result[6]
                }
            return None
            
        except Error as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_properties(self, listing_type: str = None, filters: Dict = None) -> List[Dict]:
        """Get properties with optional filters"""
        try:
            cursor = self.connection.cursor()
            
            query = '''
                SELECT p.*, u.first_name, u.last_name, u.phone, u.email
                FROM properties p
                LEFT JOIN users u ON p.agent_id = u.id
                WHERE p.status = 'available'
            '''
            params = []
            
            if listing_type:
                query += ' AND p.listing_type = %s'
                params.append(listing_type)
            
            if filters:
                if filters.get('min_price'):
                    query += ' AND p.price >= %s'
                    params.append(filters['min_price'])
                if filters.get('max_price'):
                    query += ' AND p.price <= %s'
                    params.append(filters['max_price'])
                if filters.get('bedrooms'):
                    query += ' AND p.bedrooms >= %s'
                    params.append(filters['bedrooms'])
                if filters.get('property_type'):
                    query += ' AND p.property_type = %s'
                    params.append(filters['property_type'])
                if filters.get('city'):
                    query += ' AND p.city LIKE %s'
                    params.append(f"%{filters['city']}%")
            
            query += ' ORDER BY p.created_at DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            properties = []
            for row in results:
                properties.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'property_type': row[3],
                    'address': row[4],
                    'city': row[5],
                    'state': row[6],
                    'zip_code': row[7],
                    'price': float(row[8]),
                    'bedrooms': row[9],
                    'bathrooms': row[10],
                    'square_feet': row[11],
                    'lot_size': float(row[12]) if row[12] else 0,
                    'year_built': row[13],
                    'listing_type': row[14],
                    'owner_id': row[15],
                    'agent_id': row[16],
                    'status': row[17],
                    'created_at': row[18],
                    'updated_at': row[19],
                    'agent_name': f"{row[20]} {row[21]}" if row[20] else "N/A",
                    'agent_phone': row[22] or "N/A",
                    'agent_email': row[23] or "N/A"
                })
            
            return properties
            
        except Error as e:
            print(f"Error getting properties: {e}")
            return []
    
    def get_property_by_id(self, property_id: int) -> Optional[Dict]:
        """Get a specific property by ID"""
        properties = self.get_properties()
        for prop in properties:
            if prop['id'] == property_id:
                return prop
        return None
    
    def create_transaction(self, property_id: int, buyer_id: int, seller_id: int, 
                          transaction_type: str, amount: float, notes: str = None) -> bool:
        """Create a new transaction"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (property_id, buyer_id, seller_id, 
                                        transaction_type, amount, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (property_id, buyer_id, seller_id, transaction_type, amount, notes))
            
            # Update property status
            new_status = 'sold' if transaction_type == 'purchase' else 'rented'
            cursor.execute('''
                UPDATE properties SET status = %s WHERE id = %s
            ''', (new_status, property_id))
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error creating transaction: {e}")
            return False
    
    def add_to_favorites(self, user_id: int, property_id: int) -> bool:
        """Add property to user's favorites"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO favorites (user_id, property_id)
                VALUES (%s, %s)
            ''', (user_id, property_id))
            cursor.close()
            return True
            
        except mysql.connector.IntegrityError:
            return False
        except Error as e:
            print(f"Error adding to favorites: {e}")
            return False
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """Get user's favorite properties"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT p.* FROM properties p
                JOIN favorites f ON p.id = f.property_id
                WHERE f.user_id = %s
            ''', (user_id,))
            
            results = cursor.fetchall()
            cursor.close()
            
            favorites = []
            for row in results:
                favorites.append({
                    'id': row[0],
                    'title': row[1],
                    'price': float(row[8]),
                    'property_type': row[3],
                    'address': row[4],
                    'city': row[5],
                    'state': row[6]
                })
            return favorites
            
        except Error as e:
            print(f"Error getting user favorites: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()