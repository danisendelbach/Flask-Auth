import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    #def get(self,user_id):
        #return str(user_id)

#Line below only required once, when creating DB.
with app.app_context():
    db.create_all()

@login_manager.user_loader
#******Wo wird diese user_id gespeichert?******
def load_user(user_id):
    user_id = int(user_id)
    user = db.session.execute(db.select(User).where(User.id==user_id)).scalar()
    return user

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method=="POST":
        hashed_password = generate_password_hash(request.form.get("password"),
                                                                   method="pbkdf2:sha256",
                                                                   salt_length=8)
        with app.app_context():
            new_user = User(
                name=request.form.get("name"),
                email=request.form.get("email"),
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()
        return redirect("/secrets")
    if request.method=="GET":
        return render_template("register.html")

@app.route('/login', methods=["POST","GET"])
def login():
    error = None
    if request.method=="POST":

        print(request.form.get("email"))

        cur_user=db.session.execute(db.select(User).where(User.email==request.form.get("email"))).scalar()
        if cur_user is None:
            error="There is no account with this email address"
            return render_template("login.html", error=error)
        elif not check_password_hash(cur_user.password, request.form.get("password")):
            error = "Incorrect Password"
            return render_template("login.html", error=error)
        else:
            login_user(cur_user)
            return redirect(url_for('secrets'))

    return render_template("login.html", error=error)

@app.route('/secrets')
@login_required
def secrets():
    print(current_user)
    #if not current_user.is_authenticated:
        #return login_manager.unauthorized()
    return render_template("secrets.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

@app.route('/download/')
@login_required
def download():
    app.config['UPLOAD_FOLDER'] = "./static/files"
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'cheat_sheet.pdf', as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
