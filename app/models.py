from . import db
from flask_login import UserMixin
from app import login
from datetime import datetime, timedelta,timezone
import sqlalchemy as sa
import sqlalchemy.orm as so


from typing import Optional
import secrets

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64),index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120),index=True, unique=True)
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(11),index=True, unique=True,nullable=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    registration_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.utcnow)
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]



    def __repr__(self):
        return '<User {}>'.format(self.username)
    def to_dict(self):
        data = {
            'id': self.id,
            'username':self.username,
            'email':self.email,
            'registration_date':self.registration_date
        }
        if self.phone_number:
            data['phone_number'] = self.phone_number
        return data
    def get_token(self, expires_in=86400): # 10 years
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.commit()

        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.session.commit()

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user



@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))



class Request(db.Model):
    __tablename__ = 'request'  
    
    request_id = db.Column(db.Integer, primary_key=True)
    request_description = db.Column(db.String(255)) 
    #platform = db.Column(db.String(80))
    facebook = db.Column(db.Boolean)
    x_twitter = db.Column(db.Boolean)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    query = db.Column(db.Text)
    language = db.Column(db.String(3),default="ar")
    number_of_tweets = db.Column(db.String(30),nullable = True)
    number_of_posts = db.Column(db.String(30),nullable = True)


    #status = db.Column(db.String(50))
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
    user = db.relationship('User', backref=db.backref('requests', lazy=True))
    
    def to_dict(self):
        data = {

            'request_id' : self.request_id,
            'request_description' :self.request_description,
            'facebook' : self.facebook,
            'x_twitter' :self.x_twitter,
            'start_date' :self.start_date,
            'end_date' : self.end_date,
            'query' : self.query,
            'language' : self.language
        }
        return data


    


class Result(db.Model):
    __tablename__ = 'result'  
    
    result_id = db.Column(db.Integer, primary_key=True)
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    request_id = db.Column(db.Integer, db.ForeignKey('request.request_id'), nullable=False)
    
    request = db.relationship('Request', backref=db.backref('results', lazy=True))
    
    def __repr__(self):
        return f"Result('{self.result_id}', '{self.generated_date}')"

class SubResult(db.Model):
    __tablename__ = 'subresult'  
    subresult_id = db.Column(db.Integer, primary_key=True) 
    result_id = db.Column(db.Integer, db.ForeignKey('result.result_id'), nullable=False)
    tweet_id = db.Column(db.String(30))
    creation_date = db.Column(db.String(100))
    text = db.Column(db.Text,nullable = False)
    language = db.Column(db.String(3))
    favorite_count = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)
    reply_count = db.Column(db.Integer)
    quote_count = db.Column(db.Integer)
    views_count = db.Column(db.Integer)
    source = db.Column(db.String(100))
    sentiment = db.Column(db.String(30),nullable = False)
    user_creation_date = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    user_username = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    user_follower_count = db.Column(db.Integer)
    user_following_count = db.Column(db.Integer)
    user_is_verified= db.Column(db.Boolean)
    user_blue_is_verified = db.Column(db.Boolean)
    user_location = db.Column(db.String(300))
    user_description = db.Column(db.String(300))
    user_number_of_tweets = db.Column(db.Integer)
    user_bot = db.Column(db.Boolean)

    subresult = db.relationship('Result', backref=db.backref('subrequests', lazy=True))
    
