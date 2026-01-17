## Productivity Dashboard API

A backend REST API for managing personal productivity tasks, built with **FastAPI** and **JWT authentication**.  
Users can register, login, and securely manage their own tasks with filtering, searching, and status tracking.

---

## 🚀 Features

### Authentication & Authorization
- User registration
- User login with JWT token
- Protected routes (users can access only their own tasks)

### Task Management
- Create tasks
- Get all tasks
- Update tasks
- Delete tasks
- Each task includes:
  - Title  
  - Description  
  - Priority (Low / Medium / High)  
  - Status (Pending / In Progress / Completed)  
  - Deadline  

### Search & Filtering
You can filter tasks using query parameters:
- Filter by status  
- Filter by priority  
- Search by title or description  

Example:

### ⏰ Overdue Handling
- Tasks whose deadline has passed and are not completed are automatically considered overdue.

### 📊 Productivity Ready
The project is structured so productivity analytics (like completion rate, task statistics, etc.) can easily be added later.

---

## 🛠 Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Pydantic
- Uvicorn

---

## 📂 Project Structure
.
├── main.py # FastAPI routes
├── models.py # Database models
├── schemas.py # Pydantic schemas
├── auth.py # JWT authentication logic
├── database.py # Database connection
├── requirements.txt
├── .gitignore
└── README.md

---

##  How to Run Locally
### 1. Clone the repository
``` in bash git clone https://github.com/SA6196/Productivity-dashboard-api.git
cd Productivity-dashboard-api
```
```2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
```
3. Install dependencies
```
pip install -r requirements.txt
```
5. Run the server
```
uvicorn main:app --reload
```
6. Open Swagger UI
```
Visit in browser:
http://127.0.0.1:8000/docs
You can test all endpoints (register, login, create task, filter, update, delete) from here.
```
The Demo video will be given in the official (gdg member's) on whatsapp.
