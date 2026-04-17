Pharmacy Management System
A web-based application designed to streamline pharmacy operations, including inventory management, sales tracking, and database administration. Built using Python (Flask) and MySQL.

🚀 Features
Inventory Management: Add, update, and track medicine stock.

Database Integration: Secure storage of records using MySQL.

Web Interface: User-friendly templates for managing pharmacy data.

Dependencies Management: Easy setup via requirements.txt.

🛠️ Tech Stack
Backend: Python 3.x, Flask

Frontend: HTML/CSS (located in templates and static)

Database: MySQL

📦 Installation & Setup
1. Clone the Repository
Bash
git clone https://github.com/Hema7613/Pharmacy-Mangement-System.git
cd Pharmacy-Mangement-System
2. Set Up a Virtual Environment (Optional but Recommended)
Bash
python -m venv venv
# Windows
source venv/Scripts/activate
# Mac/Linux
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Database Configuration
Open your MySQL terminal or a tool like phpMyAdmin.

Create a new database.

Import the provided SQL schema:

SQL
SOURCE pharmacy_db.sql;
Update the database connection credentials in app.py (username, password, and database name).

5. Run the Application
Bash
python app.py
The application will be available at http://127.0.0.1:5000/.

📁 Project Structure
app.py: The main Flask application script.

pharmacy_db.sql: Database schema and initial data.

templates/: HTML files for the web interface.

static/: CSS, JavaScript, and image assets.

requirements.txt: List of Python packages required for the project.
