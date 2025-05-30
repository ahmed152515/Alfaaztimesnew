# AlfaazTimes News Channel Website

## Setup Instructions

### 1. Install Dependencies
```
pip install -r requirements.txt
```

### 2. Run the Flask App
```
python app.py
```

### 3. API Endpoints
- **Admin Login:** `POST /admin/login` (JSON: username, password)
- **User Signup:** `POST /user/signup` (JSON: username, password)
- **User Login:** `POST /user/login` (JSON: username, password)

### 4. MongoDB Atlas
- The app is connected to MongoDB Atlas using the provided connection string.

---

Next steps: Frontend (HTML/CSS/JS) for login/signup pages. 