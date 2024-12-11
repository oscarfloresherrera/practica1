from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo para roles
class Role(db.Model):
    __tablename__ = "tbRoles"
    PK_Role = db.Column(db.Integer, primary_key=True)
    roleName = db.Column(db.String(25), nullable=False)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    users = db.relationship('User', backref='role', lazy=True)  # Relación con User


# Modelo para usuarios
class User(db.Model):
    __tablename__ = "tbUsers"
    PK_User = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    FK_Role = db.Column(db.Integer, db.ForeignKey("tbRoles.PK_Role"), nullable=False)
    userName = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)


# Modelo para clientes
class Client(db.Model):
    __tablename__ = "tbClients"
    PK_client = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(15), nullable=False)
    lastName = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(50))
    birthDate = db.Column(db.String(30))
    phoneNumber = db.Column(db.BigInteger)
    email = db.Column(db.String(30), unique=True)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    bills = db.relationship('Bill', backref='client', lazy=True)  # Relación con Bill


# Modelo para métodos de pago
class PaymentMethod(db.Model):
    __tablename__ = "tbPaymentMethods"
    PK_paymentMethod = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    anotherDetails = db.Column(db.Text)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    bills = db.relationship('Bill', backref='payment_method', lazy=True)  # Relación con Bill


# Modelo para facturas
class Bill(db.Model):
    __tablename__ = "tbBills"
    PK_bill = db.Column(db.Integer, primary_key=True)
    FK_client = db.Column(db.Integer, db.ForeignKey("tbClients.PK_client"), nullable=False)
    FK_paymentMethod = db.Column(db.Integer, db.ForeignKey("tbPaymentMethods.PK_paymentMethod"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    details = db.relationship('Detail', backref='bill', lazy=True)  # Relación con Detail


# Modelo para categorías
class Category(db.Model):
    __tablename__ = "tbCategories"
    PK_category = db.Column(db.Integer, primary_key=True)
    cathegoryName = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(40))
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    products = db.relationship('Product', backref='category', lazy=True)  # Relación con Product


# Modelo para productos
class Product(db.Model):
    __tablename__ = "tbProducts"
    PK_product = db.Column(db.Integer, primary_key=True)
    FK_category = db.Column(db.Integer, db.ForeignKey("tbCategories.PK_category"), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
    details = db.relationship('Detail', backref='product', lazy=True)  # Relación con Detail


# Modelo para detalles
class Detail(db.Model):
    __tablename__ = "tbDetails"
    PK_detail = db.Column(db.Integer, primary_key=True)
    FK_bill = db.Column(db.Integer, db.ForeignKey("tbBills.PK_bill"), nullable=False)
    FK_producto = db.Column(db.Integer, db.ForeignKey("tbProducts.PK_product"), nullable=False)
    createdAt = db.Column(db.Date, nullable=False)
    updatedAt = db.Column(db.Date)
    state = db.Column(db.Boolean, default=True)
