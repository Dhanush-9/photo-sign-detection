"""
app.py

This is main flask app
helps in home page navigation, collects user data
and saves file like sign and photo to disk, 
and user information in SQLite
"""


import os
import sqlite3
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from database.db_setup import get_connection, init_db, DB_PATH
from matching.signature_matcher import find_best_match

#file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNATURE_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "sign")
PHOTO_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "photo")
VERIFY_TMP_DIR = os.path.join(BASE_DIR, "static", "uploads", "verify_temp")

def get_static_path(file_path):
    """
    Convert a file path into a path that Flask's url_for('static')
    can use.
    """
    file_path = file_path.replace("\\", "/")

    if file_path.startswith("static/"):
        file_path = file_path[7:]

    return file_path

#supported extensions
ALLOWED_EXTS = {"png", "jpg", "jpeg"}

#load secret var from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_KEY", "default-key")


@app.route("/")
def home():
    return render_template("home.html")


def allowed_file(filename):
    if "." in filename:
        ext = filename.split(".")[-1].lower()
        
        if ext in ALLOWED_EXTS:
            return True

    return False

def read_user_data(request):
    """extract user data from request"""
    userInfo = {
        "name" : request.form.get("name", "").strip(),
        "email" : request.form.get("email", "").strip(),
        "contact" : request.form.get("contact", "").strip(),
        "location" : request.form.get("location", "").strip(),
        "sign_file" : request.files.get("signature"),
        "photo_file" : request.files.get("photo")
    }

    return userInfo

def validate_data(data):
    """Validate the extracted data, return(if_valid, error_msg)"""
    err_msg = None
    if not data["name"] or not data["email"]:
         err_msg = "Name and Email required."
         return False, err_msg
    
    sign = data["sign_file"]
    if not sign or sign.filename == "":
         err_msg = "Please upload a signature."
         return False, err_msg
    
    photo = data["photo_file"]
    if not photo or photo.filename == "":
         err_msg = "Please upload a photo."
         return False, err_msg
    
    if not (allowed_file(sign.filename) and allowed_file(photo.filename)):
         err_msg = "Only JPG/PNG/JPEG file format are allowed."
         return False, err_msg
    
    return True, None

def save_reg_files(data):
     """save file securely and return relative paths of sign and photo."""
     safe_email = secure_filename(data["email"])

     #extract extensions
     sig_ext = data["sign_file"].filename.split(".")[-1].lower()
     photo_ext = data["photo_file"].filename.split(".")[-1].lower()

     sign_filename = f"{safe_email}_sign.{sig_ext}"
     photo_filename = f"{safe_email}_photo.{photo_ext}"

     sign_path = os.path.join(SIGNATURE_UPLOAD_DIR, sign_filename)
     photo_path = os.path.join(PHOTO_UPLOAD_DIR, photo_filename)

     data["sign_file"].save(sign_path)
     data["photo_file"].save(photo_path)

     relative_paths = {
          "sign_path" : os.path.relpath(sign_path, BASE_DIR),
          "photo_path" : os.path.relpath(photo_path, BASE_DIR)
     }

     return relative_paths

@app.route("/register", methods=["GET", "POST"])
def register():

    #the method is GET
    if request.method == "GET":
        return render_template("register.html")
    
    #the method is POST

    #Step 1 - Read user data
    userData = read_user_data(request)

    #Step 2 - Validate user data
    is_valid, err_msg = validate_data(userData)
    if not is_valid:
        flash(err_msg)
        return redirect(url_for("register"))

    #Step 3 - Save Files
    file_paths = save_reg_files(userData)

    #Step 4 - Store in Database
    try:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO users (name, email, contact, location, sign_path, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                userData["name"],
                userData["email"],
                userData["contact"],
                userData["location"],
                file_paths["sign_path"],
                file_paths["photo_path"]
            ),
        )
        conn.commit()

    except sqlite3.Error:
        flash("Error occurred, Email is already registered.")
        return redirect(url_for("register"))
    
    flash(f"Registered {userData["name"]} successfully!")
    return redirect(url_for("home"))

@app.route("/verify-signature", methods=["GET", "POST"])
def verify_signature():

    #show verification page
    if request.method == "GET":
        return render_template("verify_signature.html")

    #the method is POST
    #get uploaded signature
    uploaded_sign = request.files.get("query_signature")

    #check if file uploaded
    if not uploaded_sign or uploaded_sign.filename == "":
        flash("Please upload a signature to verify.")
        return redirect(url_for("verify_signature"))

    #check file format
    if not allowed_file(uploaded_sign.filename):
        flash("Only JPG, PNG, JPEG file format are allowed.")
        return redirect(url_for("verify_signature"))

    #save the uploaded sign temporarily
    os.makedirs(VERIFY_TMP_DIR, exist_ok=True)


    extension = uploaded_sign.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"

    uploaded_path = os.path.join(VERIFY_TMP_DIR, filename)
    uploaded_sign.save(uploaded_path)

    #get all users from database to compare against
    conn = get_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    if not users:
        flash("No users are registered yet.")
        return redirect(url_for("verify_signature"))

    try:
        best_user, similarity_score = find_best_match(
            uploaded_path,
            users,
            BASE_DIR
        )

    except ValueError as e:
        flash(str(e))
        return redirect(url_for("verify_signature"))

    #convert score (e.g. 0.73) to percentage (e.g. 73%)
    score_percent = round(max(similarity_score, 0) * 100, 1)

    return render_template(
        "verify_signature_result.html",
        matched=best_user is not None,
        user=best_user,
        score=score_percent,
        query_image=get_static_path(os.path.relpath(uploaded_path, BASE_DIR)),
        matched_sign_image=get_static_path(best_user["sign_path"])
        if best_user else None,
    )

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()

    app.run(debug=True)

