from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



from .models import db, Client, Product, Category, Detail, Bill,PaymentMethod,User
