from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import os


# ==================================================
# APP CONFIGURATION
# ==================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "eswar-portfolio-secret-key-change-later"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Maximum upload size = 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ==================================================
# UPLOAD CONFIGURATION
# ==================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Create uploads folder automatically
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# Allowed image formats
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# ==================================================
# DATABASE
# ==================================================

db = SQLAlchemy(app)


# ==================================================
# LOGIN MANAGER
# ==================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


# ==================================================
# ADMIN TABLE
# ==================================================

class Admin(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


# ==================================================
# PROFILE TABLE
# ==================================================

class Profile(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    role = db.Column(
        db.String(200)
    )

    about = db.Column(
        db.Text
    )

    email = db.Column(
        db.String(200)
    )

    github = db.Column(
        db.String(300)
    )

    linkedin = db.Column(
        db.String(300)
    )

    # ----------------------------------------------
    # PROFILE PHOTO
    # ----------------------------------------------

    profile_photo = db.Column(
        db.String(300),
        default="profile.jpg"
    )


# ==================================================
# SKILLS TABLE
# ==================================================

class Skill(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )


# ==================================================
# PROJECT TABLE
# ==================================================

class Project(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    github = db.Column(
        db.String(300)
    )

    demo = db.Column(
        db.String(300)
    )


# ==================================================
# LOAD USER
# ==================================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        Admin,
        int(user_id)
    )


# ==================================================
# PUBLIC WEBSITE
# ==================================================

@app.route("/")
def home():

    profile = Profile.query.first()

    skills = Skill.query.all()

    projects = Project.query.all()

    return render_template(
        "index.html",
        profile=profile,
        skills=skills,
        projects=projects
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Already logged in
    if current_user.is_authenticated:

        return redirect(
            url_for("admin")
        )


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        admin = Admin.query.filter_by(
            username=username
        ).first()


        if admin and check_password_hash(
            admin.password,
            password
        ):

            login_user(admin)

            return redirect(
                url_for("admin")
            )


        flash(
            "Invalid username or password",
            "error"
        )


    return render_template(
        "login.html"
    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/admin")
@login_required
def admin():

    profile = Profile.query.first()

    skills = Skill.query.all()

    projects = Project.query.all()

    return render_template(
        "admin.html",
        profile=profile,
        skills=skills,
        projects=projects
    )


# ==================================================
# UPDATE PROFILE DETAILS
# ==================================================

@app.route(
    "/admin/profile",
    methods=["POST"]
)
@login_required
def update_profile():

    profile = Profile.query.first()


    if not profile:

        flash(
            "Profile not found.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    profile.name = request.form.get(
        "name"
    )

    profile.role = request.form.get(
        "role"
    )

    profile.about = request.form.get(
        "about"
    )

    profile.email = request.form.get(
        "email"
    )

    profile.github = request.form.get(
        "github"
    )

    profile.linkedin = request.form.get(
        "linkedin"
    )


    db.session.commit()


    flash(
        "Profile updated successfully!",
        "success"
    )


    return redirect(
        url_for("admin")
    )


# ==================================================
# CHANGE PROFILE PHOTO
# ==================================================

@app.route(
    "/admin/profile/photo",
    methods=["POST"]
)
@login_required
def update_profile_photo():

    profile = Profile.query.first()


    if not profile:

        flash(
            "Profile not found.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    # Get uploaded file
    file = request.files.get(
        "profile_photo"
    )


    # Check whether file was selected
    if not file or file.filename == "":

        flash(
            "Please select a profile photo.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    # Check extension
    if not allowed_file(
        file.filename
    ):

        flash(
            "Only JPG, JPEG, PNG and WEBP images are allowed.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    # Secure original filename
    original_filename = secure_filename(
        file.filename
    )


    # Get extension
    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()


    # Always use one fixed filename
    # This makes replacement simple
    new_filename = "profile." + extension


    new_filepath = os.path.join(
        UPLOAD_FOLDER,
        new_filename
    )


    # ----------------------------------------------
    # DELETE OLD PROFILE PHOTO
    # ----------------------------------------------

    old_filename = profile.profile_photo


    if old_filename:

        old_filepath = os.path.join(
            UPLOAD_FOLDER,
            old_filename
        )


        if os.path.exists(
            old_filepath
        ):

            # Don't delete if same file
            if os.path.abspath(
                old_filepath
            ) != os.path.abspath(
                new_filepath
            ):

                os.remove(
                    old_filepath
                )


    # ----------------------------------------------
    # SAVE NEW PHOTO
    # ----------------------------------------------

    file.save(
        new_filepath
    )


    # ----------------------------------------------
    # UPDATE DATABASE
    # ----------------------------------------------

    profile.profile_photo = new_filename


    db.session.commit()


    flash(
        "Profile photo changed successfully!",
        "success"
    )


    return redirect(
        url_for("admin")
    )


# ==================================================
# ADD SKILL
# ==================================================

@app.route(
    "/admin/skill/add",
    methods=["POST"]
)
@login_required
def add_skill():

    name = request.form.get(
        "name"
    )


    if name:

        name = name.strip()


        if name:

            skill = Skill(
                name=name
            )

            db.session.add(
                skill
            )

            db.session.commit()


            flash(
                "Skill added successfully!",
                "success"
            )


    return redirect(
        url_for("admin")
    )


# ==================================================
# DELETE SKILL
# ==================================================

@app.route(
    "/admin/skill/delete/<int:id>"
)
@login_required
def delete_skill(id):

    skill = db.session.get(
        Skill,
        id
    )


    if skill:

        db.session.delete(
            skill
        )

        db.session.commit()


        flash(
            "Skill deleted successfully!",
            "success"
        )


    return redirect(
        url_for("admin")
    )


# ==================================================
# ADD PROJECT
# ==================================================

@app.route(
    "/admin/project/add",
    methods=["POST"]
)
@login_required
def add_project():

    title = request.form.get(
        "title"
    )

    description = request.form.get(
        "description"
    )

    github = request.form.get(
        "github"
    )

    demo = request.form.get(
        "demo"
    )


    if not title:

        flash(
            "Project title is required.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    project = Project(

        title=title.strip(),

        description=description,

        github=github,

        demo=demo
    )


    db.session.add(
        project
    )

    db.session.commit()


    flash(
        "Project added successfully!",
        "success"
    )


    return redirect(
        url_for("admin")
    )


# ==================================================
# DELETE PROJECT
# ==================================================

@app.route(
    "/admin/project/delete/<int:id>"
)
@login_required
def delete_project(id):

    project = db.session.get(
        Project,
        id
    )


    if project:

        db.session.delete(
            project
        )

        db.session.commit()


        flash(
            "Project deleted successfully!",
            "success"
        )


    return redirect(
        url_for("admin")
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

with app.app_context():

    db.create_all()


    # ----------------------------------------------
    # CREATE ADMIN
    # ----------------------------------------------

    if not Admin.query.first():

        admin = Admin(

            username="eswar",

            password=generate_password_hash(
                "eswar123"
            )
        )

        db.session.add(
            admin
        )


    # ----------------------------------------------
    # CREATE PROFILE
    # ----------------------------------------------

    if not Profile.query.first():

        profile = Profile(

            name="ESWAR",

            role="AI/ML Engineer | Python Developer",

            about=(
                "B.Tech Computer Science student passionate "
                "about Artificial Intelligence, Machine Learning "
                "and Software Development."
            ),

            email="eswar@example.com",

            github="https://github.com/",

            linkedin="https://linkedin.com/",

            profile_photo="profile.jpg"
        )

        db.session.add(
            profile
        )


    # ----------------------------------------------
    # DEFAULT SKILLS
    # ----------------------------------------------

    if Skill.query.count() == 0:

        skills = [

            "Python",

            "Machine Learning",

            "Flask",

            "SQL",

            "HTML & CSS",

            "Git",

            "ServiceNow"

        ]


        for skill_name in skills:

            db.session.add(
                Skill(
                    name=skill_name
                )
            )


    db.session.commit()


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )