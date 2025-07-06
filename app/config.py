import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '3c04847aa2ea1bcd655cf387643fa9410b8eef987832d535779664b659156eeb'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://ibrahim:ibrahim@localhost/flaskdb' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
