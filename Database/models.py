from mongoengine import *
from .db import db
from datetime import *
from flask_bcrypt import generate_password_hash, check_password_hash


class user_db(db.Document, db.DynamicDocument):
    user_name = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    email = db.StringField(required=True)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class group_db(db.Document, db.DynamicDocument):
    creator = db.StringField(required=True)
    group_name = db.StringField(required=True, unique=True)
    member = db.ListField(db.StringField(), required=True, default=set)
    moderator = db.ListField(db.StringField(), required=True)
    admin = db.ListField(db.StringField(), required=True)
    type = db.StringField(required=True, choices=["PRIVATE", "PUBLIC"])


class posts_db(db.Document, db.DynamicDocument):
    group_name = db.StringField(required=True)
    type = db.StringField(required=True)
    posted_by = db.StringField(required=True)
    post = db.StringField(required=True)
    status = db.StringField(default="IN-TRANSIT")
    approved_by = db.StringField()
    date = DateField(default=date.today)


class comment_db(db.Document, db.DynamicDocument):
    post_id = db.StringField(required=True)
    post_of = db.StringField(required=True)
    group_name = db.StringField(required=True)
    user_name = db.StringField(required=True)
    comment = db.StringField(required=True)



