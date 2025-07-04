# RealEstate Pro - Complete Real Estate Management System

## Description

RealEstate Pro is a comprehensive real estate management application built with Python and Tkinter. It features both a customer-facing interface for browsing and purchasing/renting properties, and a complete back-office administration system for managing all aspects of the real estate business.

## Features

### Customer Interface
- Browse properties for sale and rent
- Advanced search and filtering
- User registration and authentication
- Property details with agent information
- Purchase and rental transactions
- Favorites system

### Admin Back-Office System
- **Admin Dashboard**: Overview with key metrics and recent activity
- **Property Management**: Add, edit, delete, and manage all properties
- **User Management**: Manage user accounts, view statistics, activate/deactivate users
- **Transaction Management**: Monitor and manage all transactions, update statuses
- **Analytics Dashboard**: Comprehensive analytics with charts and reports
- **System Administration**: Complete control over the real estate platform

## Technologies Used

- Python 3
- Tkinter (GUI)
- MySQL (Database)
- `mysql-connector-python` (Python MySQL driver)
- Matplotlib (for analytics charts - optional)

## Project Structure

```
.
├── main.py                    # Main application entry point
├── config.py                  # Configuration settings
├── database.py                # Database management and all data operations
├── auth.py                    # Customer authentication
├── admin_auth.py              # Admin authentication
├── admin_dashboard.py         # Main admin dashboard
├── property_management.py     # Property CRUD operations
├── user_management.py         # User management interface
├── transaction_management.py  # Transaction monitoring and management
├── analytics_dashboard.py     # Analytics and reporting
├── property_details.py        # Property details window
├── ui_components.py           # Custom UI components
├── README.md                  # Project documentation
└── capture/                   # Screenshots
    ├── HomePage.png
    ├── signIn.png
    ├── singnUp.png
    ├── detailsProperty.png
    └── unvailablefilter.png
```

## Admin Features

### Dashboard Overview
- Real-time statistics (total properties, users, transactions, revenue)
- Recent activity feed
- Quick access to all management modules
- System information

### Property Management
- View all properties in a searchable table
- Add new properties with complete details
- Edit existing property information
- Delete properties (with confirmation)
- Property status management (available, sold, rented, pending)

### User Management
- View all registered users
- User statistics (properties owned, transactions, favorites)
- Activate/deactivate user accounts
- Edit user information
- Delete users (with cascade deletion of related data)
- Add new users manually

### Transaction Management
- Monitor all transactions (purchases and rentals)
- Filter by status (pending, completed, cancelled) and type
- Update transaction statuses
- Cancel transactions (makes property available again)
- Delete transaction records
- View complete transaction details

### Analytics Dashboard
- Revenue analytics (total, monthly, yearly)
- Property performance metrics
- User growth statistics
- Sales conversion rates
- Top performing properties
- Market trends and insights

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- MySQL Server (XAMPP, WAMP, or standalone MySQL)

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/Lucky-On-13/realestate-pro.git
cd realestate-pro
```

2. **Install required packages:**
```bash
pip install mysql-connector-python
```

3. **Set up MySQL database:**
   - Start your MySQL server (XAMPP/WAMP or standalone)
   - Update database credentials in `config.py`:
   ```python
   DB_HOST = "localhost"
   DB_PORT = 3306
   DB_NAME = "real_estate_db"
   DB_USER = "root"
   DB_PASSWORD = ""  # Set your MySQL password here
   ```

4. **Run the application:**
```bash
python main.py
```

## Default Admin Credentials

When you first run the application, a default admin account is created:
- **Username:** `admin`
- **Password:** `admin123`

**Important:** Change these credentials immediately after first login for security.

## Usage

### For Customers
1. Launch the application
2. Browse properties using the "For Sale" or "For Rent" tabs
3. Use search filters to find specific properties
4. Click "Login / Sign Up" to create an account or log in
5. View property details and make transactions
6. Add properties to favorites

### For Administrators
1. Click the "Admin" button in the top-right corner
2. Log in with admin credentials
3. Access the admin dashboard with all management tools
4. Use the different tabs to manage properties, users, and transactions
5. View analytics and system reports

## Database Schema

The application automatically creates the following tables:
- `admins` - Admin user accounts
- `users` - Customer accounts
- `properties` - Property listings
- `transactions` - Purchase and rental transactions
- `favorites` - User favorite properties
- `property_images` - Property image references (for future enhancement)

## Security Features

- Password hashing using SHA-256
- Admin and user role separation
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- User session management

## Future Enhancements

- Image upload and management for properties
- Email notifications for transactions
- Advanced reporting with PDF export
- Property comparison features
- Map integration for property locations
- Mobile-responsive web interface
- API for third-party integrations

## Collaborators

- [Victoire Luc Ngami](https://github.com/Lucky-On-13)  
- [Espoir Assounga](https://github.com/collaborator-github-username)

## Repository

Project GitHub repository: [https://github.com/Lucky-On-13/realestate-pro.git](https://github.com/Lucky-On-13/realestate-pro.git)


## Support

For support or questions, please open an issue on the GitHub repository or contact the development team.

## Screenshots

### Customer Interface
![Home Page](capture/HomePage.png)
![Sign In](capture/signIn.png)
![Property Details](capture/detailsProperty.png)

### Admin Interface
The admin interface includes comprehensive dashboards for managing all aspects of the real estate business, with intuitive forms and data visualization tools.