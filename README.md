# Online Voting System

A web-based Online Voting System built with Django that enables secure and efficient digital voting. The system allows administrators to manage elections and candidates while providing voters with a simple interface to cast their votes.

## Features

* User authentication and authorization
* Secure voter registration
* Candidate management
* Election management
* One vote per voter
* Real-time vote counting
* Admin dashboard
* SQLite database integration
* Responsive user interface

## Technologies Used

* Python
* Django
* HTML5
* CSS3
* Bootstrap
* JavaScript
* SQLite

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR_USERNAME/voting-system.git
   ```

2. Navigate to the project directory:

   ```bash
   cd voting-system
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Open your browser and visit:

   ```text
   http://127.0.0.1:8000/
   ```

## Project Structure

```text
voting-system/
│
├── manage.py
├── db.sqlite3
├── requirements.txt
├── voting_system/
├── templates/
├── static/
└── media/
```

## Future Enhancements

* Email verification
* Election scheduling
* Result analytics and charts
* Multi-factor authentication
* Online voter verification

## Author

Zensi Sukhadiya
