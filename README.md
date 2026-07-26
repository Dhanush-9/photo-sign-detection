# Automatic Signature and Photo Detection using AI

A lightweight Flask web application that handles user registration, custom file uploads (signatures and profile photos). The app stores data securely in a local SQLite database and verifies uploaded signatures and photos using OpenCV-based image matching.

---

## Features

- User registration with profile photo and signature upload.
- SQLite database for storing user information.
- Signature verification using OpenCV template matching.
- Photo verification using Haar Cascade face detection and OpenCV template matching.
- Signature detection from full documents using a YOLOv5 model.
- Secure file upload validation.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Dhanush-9/photo-sign-detection.git
cd photo-sign-detection
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
FLASK_KEY=your_secret_key_here
```

---

## Initialize the Database

Before running the application, create the SQLite database.

```bash
python database/db_setup.py
```

This creates the required database and tables.

---

## Run the Application

Start the Flask server.

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

## Technologies Used

- Python
- Flask
- SQLite
- OpenCV
- YOLOv5
- HTML
- CSS
- JavaScript

---

## Future Improvements

- OCR for extracting text from uploaded documents.
- User authentication and login system.
