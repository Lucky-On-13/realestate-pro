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
            cursor.execute("DROP TABLE IF EXISTS admins")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # Admins table
            cursor.execute('''
                CREATE TABLE admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
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
            
            # Create default admin user
            admin_password_hash = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO admins (username, email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin', 'admin@realestate.com', admin_password_hash, 'Admin', 'User'))
            
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
    
    # Admin authentication methods
    def authenticate_admin(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate admin user"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, first_name, last_name
                FROM admins WHERE username = %s AND password_hash = %s AND is_active = TRUE
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'first_name': result[3],
                    'last_name': result[4]
                }
            return None
            
        except Error as e:
            print(f"Error authenticating admin: {e}")
            return None
    
    # Admin dashboard methods
    def get_admin_statistics(self) -> Dict:
        """Get statistics for admin dashboard"""
        try:
            cursor = self.connection.cursor()
            
            # Total properties
            cursor.execute("SELECT COUNT(*) FROM properties")
            total_properties = cursor.fetchone()[0]
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
            total_users = cursor.fetchone()[0]
            
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_transactions = cursor.fetchone()[0]
            
            # Monthly revenue
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE MONTH(transaction_date) = MONTH(CURRENT_DATE()) 
                AND YEAR(transaction_date) = YEAR(CURRENT_DATE())
                AND status = 'completed'
            ''')
            monthly_revenue = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_properties': total_properties,
                'total_users': total_users,
                'total_transactions': total_transactions,
                'monthly_revenue': float(monthly_revenue) if monthly_revenue else 0
            }
            
        except Error as e:
            print(f"Error getting admin statistics: {e}")
            return {
                'total_properties': 0,
                'total_users': 0,
                'total_transactions': 0,
                'monthly_revenue': 0
            }
    
    def get_recent_activities(self, limit: int = 20) -> List[str]:
        """Get recent system activities"""
        try:
            cursor = self.connection.cursor()
            
            activities = []
            
            # Recent transactions
            cursor.execute('''
                SELECT t.transaction_type, t.amount, t.transaction_date, 
                       p.title, u.first_name, u.last_name
                FROM transactions t
                JOIN properties p ON t.property_id = p.id
                JOIN users u ON t.buyer_id = u.id
                ORDER BY t.transaction_date DESC
                LIMIT %s
            ''', (limit // 2,))
            
            transactions = cursor.fetchall()
            for trans in transactions:
                activity = f"{trans[4]} {trans[5]} {trans[0]}d '{trans[3]}' for ${trans[1]:,.0f}"
                activities.append(activity)
            
            # Recent user registrations
            cursor.execute('''
                SELECT first_name, last_name, created_at, user_type
                FROM users
                ORDER BY created_at DESC
                LIMIT %s
            ''', (limit // 2,))
            
            users = cursor.fetchall()
            for user in users:
                activity = f"New {user[3]} registered: {user[0]} {user[1]}"
                activities.append(activity)
            
            cursor.close()
            
            # Sort by timestamp and return
            return activities[:limit]
            
        except Error as e:
            print(f"Error getting recent activities: {e}")
            return []
    
    # Property management methods
    def get_all_properties_admin(self) -> List[Dict]:
        """Get all properties for admin management"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT p.*, 
                       CONCAT(owner.first_name, ' ', owner.last_name) as owner_name,
                       CONCAT(agent.first_name, ' ', agent.last_name) as agent_name
                FROM properties p
                LEFT JOIN users owner ON p.owner_id = owner.id
                LEFT JOIN users agent ON p.agent_id = agent.id
                ORDER BY p.created_at DESC
            ''')
            
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
                    'owner_name': row[20] or 'N/A',
                    'agent_name': row[21] or 'N/A'
                })
            
            return properties
            
        except Error as e:
            print(f"Error getting properties for admin: {e}")
            return []
    
    def get_property_by_id_admin(self, property_id: int) -> Optional[Dict]:
        """Get property by ID for admin"""
        properties = self.get_all_properties_admin()
        for prop in properties:
            if prop['id'] == property_id:
                return prop
        return None
    
    def create_property(self, data: Dict) -> bool:
        """Create new property"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT INTO properties (title, description, property_type, address, city, state,
                                      zip_code, price, bedrooms, bathrooms, square_feet, lot_size,
                                      year_built, listing_type, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['title'], data.get('description'), data['property_type'],
                data['address'], data['city'], data['state'], data['zip_code'],
                data['price'], data.get('bedrooms'), data.get('bathrooms'),
                data.get('square_feet'), data.get('lot_size'), data.get('year_built'),
                data['listing_type'], data.get('status', 'available')
            ))
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error creating property: {e}")
            return False
    
    def update_property(self, property_id: int, data: Dict) -> bool:
        """Update existing property"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                UPDATE properties SET
                    title = %s, description = %s, property_type = %s, address = %s,
                    city = %s, state = %s, zip_code = %s, price = %s,
                    bedrooms = %s, bathrooms = %s, square_feet = %s, lot_size = %s,
                    year_built = %s, listing_type = %s, status = %s
                WHERE id = %s
            ''', (
                data['title'], data.get('description'), data['property_type'],
                data['address'], data['city'], data['state'], data['zip_code'],
                data['price'], data.get('bedrooms'), data.get('bathrooms'),
                data.get('square_feet'), data.get('lot_size'), data.get('year_built'),
                data['listing_type'], data.get('status', 'available'), property_id
            ))
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error updating property: {e}")
            return False
    
    def delete_property(self, property_id: int) -> bool:
        """Delete property"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM properties WHERE id = %s", (property_id,))
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error deleting property: {e}")
            return False
    
    # User management methods
    def get_all_users_admin(self) -> List[Dict]:
        """Get all users for admin management"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT id, username, email, first_name, last_name, phone, user_type, created_at, is_active
                FROM users
                ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            cursor.close()
            
            users = []
            for row in results:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'first_name': row[3],
                    'last_name': row[4],
                    'phone': row[5],
                    'user_type': row[6],
                    'created_at': row[7],
                    'is_active': row[8]
                })
            
            return users
            
        except Error as e:
            print(f"Error getting users for admin: {e}")
            return []
    
    def get_user_by_id_admin(self, user_id: int) -> Optional[Dict]:
        """Get user by ID for admin"""
        users = self.get_all_users_admin()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Properties owned
            cursor.execute("SELECT COUNT(*) FROM properties WHERE owner_id = %s", (user_id,))
            properties_owned = cursor.fetchone()[0]
            
            # Transactions
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE buyer_id = %s OR seller_id = %s", (user_id, user_id))
            transactions = cursor.fetchone()[0]
            
            # Favorites
            cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = %s", (user_id,))
            favorites = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'properties_owned': properties_owned,
                'transactions': transactions,
                'favorites': favorites
            }
            
        except Error as e:
            print(f"Error getting user statistics: {e}")
            return {'properties_owned': 0, 'transactions': 0, 'favorites': 0}
    
    def create_user_admin(self, data: Dict) -> bool:
        """Create new user (admin function)"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(data['password'])
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, last_name, phone, user_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['username'], data['email'], password_hash,
                data['first_name'], data['last_name'], data.get('phone'), data['user_type']
            ))
            
            cursor.close()
            return True
            
        except mysql.connector.IntegrityError:
            return False
        except Error as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user_admin(self, user_id: int, data: Dict) -> bool:
        """Update user (admin function)"""
        try:
            cursor = self.connection.cursor()
            
            if data.get('password'):
                # Update with new password
                password_hash = self.hash_password(data['password'])
                cursor.execute('''
                    UPDATE users SET username = %s, email = %s, password_hash = %s,
                                   first_name = %s, last_name = %s, phone = %s, user_type = %s
                    WHERE id = %s
                ''', (
                    data['username'], data['email'], password_hash,
                    data['first_name'], data['last_name'], data.get('phone'),
                    data['user_type'], user_id
                ))
            else:
                # Update without changing password
                cursor.execute('''
                    UPDATE users SET username = %s, email = %s, first_name = %s,
                                   last_name = %s, phone = %s, user_type = %s
                    WHERE id = %s
                ''', (
                    data['username'], data['email'], data['first_name'],
                    data['last_name'], data.get('phone'), data['user_type'], user_id
                ))
            
            cursor.close()
            return True
            
        except mysql.connector.IntegrityError:
            return False
        except Error as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Update user active status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error updating user status: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and all associated data"""
        try:
            cursor = self.connection.cursor()
            
            # Delete in order due to foreign key constraints
            cursor.execute("DELETE FROM favorites WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM transactions WHERE buyer_id = %s OR seller_id = %s", (user_id, user_id))
            cursor.execute("DELETE FROM properties WHERE owner_id = %s OR agent_id = %s", (user_id, user_id))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error deleting user: {e}")
            return False
    
    # Transaction management methods
    def get_all_transactions_admin(self, status_filter: str = None, type_filter: str = None) -> List[Dict]:
        """Get all transactions for admin management"""
        try:
            cursor = self.connection.cursor()
            
            query = '''
                SELECT t.*, p.title as property_title, p.address as property_address,
                       CONCAT(buyer.first_name, ' ', buyer.last_name) as buyer_name,
                       buyer.email as buyer_email,
                       CONCAT(seller.first_name, ' ', seller.last_name) as seller_name,
                       seller.email as seller_email
                FROM transactions t
                JOIN properties p ON t.property_id = p.id
                JOIN users buyer ON t.buyer_id = buyer.id
                JOIN users seller ON t.seller_id = seller.id
                WHERE 1=1
            '''
            params = []
            
            if status_filter:
                query += " AND t.status = %s"
                params.append(status_filter)
            
            if type_filter:
                query += " AND t.transaction_type = %s"
                params.append(type_filter)
            
            query += " ORDER BY t.transaction_date DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            
            transactions = []
            for row in results:
                transactions.append({
                    'id': row[0],
                    'property_id': row[1],
                    'buyer_id': row[2],
                    'seller_id': row[3],
                    'transaction_type': row[4],
                    'amount': float(row[5]),
                    'transaction_date': row[6],
                    'status': row[7],
                    'notes': row[8],
                    'property_title': row[9],
                    'property_address': row[10],
                    'buyer_name': row[11],
                    'buyer_email': row[12],
                    'seller_name': row[13],
                    'seller_email': row[14]
                })
            
            return transactions
            
        except Error as e:
            print(f"Error getting transactions for admin: {e}")
            return []
    
    def get_transaction_by_id_admin(self, transaction_id: int) -> Optional[Dict]:
        """Get transaction by ID for admin"""
        transactions = self.get_all_transactions_admin()
        for trans in transactions:
            if trans['id'] == transaction_id:
                return trans
        return None
    
    def update_transaction_status(self, transaction_id: int, status: str) -> bool:
        """Update transaction status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE transactions SET status = %s WHERE id = %s", (status, transaction_id))
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error updating transaction status: {e}")
            return False
    
    def cancel_transaction(self, transaction_id: int) -> bool:
        """Cancel transaction and make property available again"""
        try:
            cursor = self.connection.cursor()
            
            # Get transaction details
            cursor.execute("SELECT property_id FROM transactions WHERE id = %s", (transaction_id,))
            result = cursor.fetchone()
            
            if result:
                property_id = result[0]
                
                # Update transaction status
                cursor.execute("UPDATE transactions SET status = 'cancelled' WHERE id = %s", (transaction_id,))
                
                # Make property available again
                cursor.execute("UPDATE properties SET status = 'available' WHERE id = %s", (property_id,))
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error cancelling transaction: {e}")
            return False
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete transaction"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    # Analytics methods
    def get_analytics_data(self) -> Dict:
        """Get comprehensive analytics data"""
        try:
            cursor = self.connection.cursor()
            
            analytics = {}
            
            # Revenue analytics
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'completed'")
            analytics['total_revenue'] = float(cursor.fetchone()[0])
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE status = 'completed' AND MONTH(transaction_date) = MONTH(CURRENT_DATE())
                AND YEAR(transaction_date) = YEAR(CURRENT_DATE())
            ''')
            analytics['monthly_sales'] = float(cursor.fetchone()[0])
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE status = 'completed' AND YEAR(transaction_date) = YEAR(CURRENT_DATE())
            ''')
            analytics['yearly_sales'] = float(cursor.fetchone()[0])
            
            # Property analytics
            cursor.execute("SELECT COUNT(*) FROM properties WHERE status IN ('sold', 'rented')")
            analytics['properties_sold'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE status = 'available'")
            analytics['active_listings'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties")
            analytics['total_properties'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE status = 'available'")
            analytics['available_properties'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE status IN ('sold', 'rented')")
            analytics['sold_properties'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(AVG(price), 0) FROM properties WHERE status = 'available'")
            analytics['avg_property_price'] = float(cursor.fetchone()[0])
            
            cursor.execute("SELECT COALESCE(AVG(price), 0) FROM transactions WHERE status = 'completed'")
            analytics['avg_sale_price'] = float(cursor.fetchone()[0])
            
            # User analytics
            cursor.execute("SELECT COUNT(*) FROM users")
            analytics['total_users'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
            analytics['active_users'] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE MONTH(created_at) = MONTH(CURRENT_DATE()) 
                AND YEAR(created_at) = YEAR(CURRENT_DATE())
            ''')
            analytics['new_users_month'] = cursor.fetchone()[0]
            
            # Calculate user growth (simplified)
            analytics['user_growth'] = 5.2  # Placeholder
            
            # Market analytics
            analytics['avg_days_market'] = 45  # Placeholder
            analytics['conversion_rate'] = 12.5  # Placeholder
            
            cursor.close()
            return analytics
            
        except Error as e:
            print(f"Error getting analytics data: {e}")
            return {}
    
    def get_top_properties(self) -> List[Dict]:
        """Get top performing properties"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT p.*, t.amount as sale_price
                FROM properties p
                JOIN transactions t ON p.id = t.property_id
                WHERE t.status = 'completed'
                ORDER BY t.amount DESC
                LIMIT 20
            ''')
            
            results = cursor.fetchall()
            cursor.close()
            
            properties = []
            for row in results:
                properties.append({
                    'id': row[0],
                    'title': row[1],
                    'property_type': row[3],
                    'price': float(row[20]),  # sale_price from transaction
                    'days_on_market': 30  # Placeholder
                })
            
            return properties
            
        except Error as e:
            print(f"Error getting top properties: {e}")
            return []
    
    # Existing methods (keep all the original methods)
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