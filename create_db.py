from main import app

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

