from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Menghubungkan SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Membuat sebuah DB
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'
    

@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        
        #Tugas #4. Menerapkan otorisasi
        users_db = User.query.all()
        for user in users_db:
            if form_login == user.login and form_password == user.password:
                return redirect("/index")
            else:
                error = "Login atau kata sandi tidak tepat"
                return render_template("login.html", error=error)
    else:
        return render_template('login.html')

@app.route("/index")
def index():
    return render_template("login.html")


if __name__=="__main__":
    app.run(debug=True)