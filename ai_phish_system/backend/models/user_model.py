from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo

bcrypt = Bcrypt()
mongo = PyMongo()

class User:
    @staticmethod
    def create_user(email, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        return mongo.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'created_at': mongo.db.command('serverStatus')['localTime']
        })

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.check_password_hash(stored_password, provided_password)
