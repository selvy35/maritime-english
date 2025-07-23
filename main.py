from flask import Flask, render_template, request

app = Flask(__name__)

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