# Anywhere - Vehicle Parking Management System

Anywhere is a full-stack web application designed to simplify vehicle parking management. It provides a seamless experience for both administrators managing parking lots and users looking to book a spot. The application features a clean, responsive black-and-white theme, real-time updates, and a clear distinction between admin and user functionalities.

## ✨ Features

#### Core Functionalities

- **User Authentication:** Secure registration and login for users, plus a pre-configured admin account.
    
- **Admin Dashboard:** A powerful interface for admins to Create, Read, Update, and Delete (CRUD) parking lots.
    
- **Real-time Monitoring:** Admins can view the live status of all parking spots across all lots.
    
- **User Management:** Admins can view a list of all registered users.
    
- **Data Analytics:** The admin dashboard includes summary statistics and charts for quick insights.
    
- **Automatic Spot Generation:** Parking spots are automatically created based on the lot capacity provided by the admin.
    

#### User-Facing Features

- **User Dashboard:** A personalized dashboard for registered users to manage their parking.
    
- **Lot Discovery:** Users can view all available parking lots, including details like address, price, and real-time spot availability.
    
- **Effortless Booking:** Users can book a parking spot with a simple form, and a spot is automatically allocated.
    
- **Spot Release & Billing:** Users can release their spot upon leaving, and the system automatically calculates the parking cost based on duration.
    
- **Reservation History:** Users can view their current and past reservations with detailed cost breakdowns.
    

#### Technical & Advanced Features

- **RESTful API:** Provides API endpoints to fetch data about parking lots and spots programmatically.
    
- **Robust Validation:** Implements both client-side (JavaScript) and server-side (Flask) validation for data integrity.
    
- **Responsive UI:** A clean, professional, and mobile-friendly black-and-white theme built with custom CSS.
    
- **Secure:** Uses password hashing to protect user credentials.
    
- **Reliable:** Features comprehensive error handling and user-friendly flash messages for a smooth experience.
    

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
    
- **Database:** SQLite
    
- **Frontend:** HTML, Vanilla CSS, Vanilla JavaScript
    
- **Templating:** Jinja2
    

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.7 or higher
    
- `pip` (Python package installer)
    
- `git` for cloning the repository
    

### Installation and Setup

1. **Clone the Repository**
    
    ```
    git clone [https://github.com/your-username/anywhere_parking_app.git](https://github.com/your-username/anywhere_parking_app.git)
    cd anywhere_parking_app
    ```
    
2. **Create and Activate Virtual Environment**
    
    ```
    # Create the virtual environment
    python -m venv venv
    
    # Activate it
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
    
3. **Install Dependencies**
    
    ```
    # Ensure you are in the root project directory
    pip install -r backend/requirements.txt
    ```
    
4. **Run the Application**
    
    ```
    cd backend
    python app.py
    ```
    
    The application will start, and the SQLite database (`parking_app.db`) will be created automatically in the `backend` folder along with a default admin user.
    
5. **Access the Application** Open your web browser and navigate to: **`http://127.0.0.1:5000`**
    

## 📖 How to Use

#### For Admin Users:

- **Login:** Use the default admin credentials:
    
    - **Username:** `admin`
        
    - **Password:** `admin123`
        
- **Manage Lots:** Navigate the dashboard to create, edit, or delete parking lots.
    
- **Monitor:** View real-time occupancy, detailed spot status, and a list of registered users.
    

#### For Regular Users:

1. **Register:** Create a new account.
    
2. **Login:** Access your personal dashboard.
    
3. **Book:** Browse available lots and book a spot by providing your vehicle number.
    
4. **Release:** When you are done, release the spot from your dashboard to check out.
    
5. **History:** View your parking history and associated costs.
    

## 📁 Project Structure

```
anywhere_parking_app/
├── backend/
│   ├── app.py              # Main Flask application logic and routes
│   ├── models.py           # SQLAlchemy database models
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── parking_app.db      # SQLite database (auto-generated)
└── frontend/
    ├── templates/          # Jinja2 HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── ...
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── main.js
```

## 🔗 API Endpoints

The application provides the following RESTful API endpoints:

- **`GET /api/lots`**: Fetches a JSON list of all parking lots with their current status.
    
- **`GET /api/lot/<id>/spots`**: Fetches a JSON list of all spots for a specific lot, including reservation details if occupied.
