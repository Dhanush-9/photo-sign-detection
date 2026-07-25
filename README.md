# Automatic Signature and Photo Detection using AI & OCR

A lightweight Flask web application that handles user registration, custom file uploads (signatures and profile photos). The app stores data securely in a local SQLite database, and verifies uploaded signatures and photos using OpenCV-based image matching.

## Progress
- **Read Data**: Extracts user registration data including text and image files.
- **Validation**: Ensures proper input extension (`.png`, `.jpg`, `.jpeg`) and required fields exist.
- **File Storage**: Saves files to disk with proper collision resolution mechanism.
- **SQLite DataBase**: Stores relative file paths and user data cleanly using SQLite.
- **Sign Verification**: Matches uploaded signatures against registered signatures using OpenCV template matching.
- **Photo Verification**: Detects faces using OpenCV Haar Cascades and matches uploaded photos against registered users using template matching.