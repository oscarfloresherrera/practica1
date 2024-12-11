from flask import Flask, render_template, request, redirect, url_for, send_file, session
from sqlalchemy.sql import text  # Importa la función text
from models import db, Client, Product, Category, Detail, Bill, PaymentMethod ,User 
from datetime import datetime
from io import BytesIO
from functools import wraps
from fpdf import FPDF
import pdfkit
import os

# Inicializar la aplicación
app = Flask(__name__)
app.config.from_object("config.Config")

# Inicializar la base de datos
db.init_app(app)

# Decorador para verificar si el usuario está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar roles
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role not in roles:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar al usuario por nombre de usuario y contraseña
        user = db.session.execute(
            text("""
            SELECT u."PK_User", u."name", u."lastName", r."roleName"
            FROM "tbUsers" u
            JOIN "tbRoles" r ON u."FK_Role" = r."PK_Role"
            WHERE u."userName" = :username AND u."password" = :password AND u."state" = TRUE
            """),
            {"username": username, "password": password}
        ).fetchone()

        if user:
            # Guardar información del usuario en la sesión
            session['user_id'] = user.PK_User
            session['user_name'] = f"{user.name} {user.lastName}"
            session['user_role'] = user.roleName
            return redirect(url_for('index'))
        else:
            # Mostrar un mensaje de error si no se encuentra al usuario
            return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template("base.html", user_role=session.get('user_role'), user_name=session.get('user_name'))


# Ruta para la página principal de productos (Empleado: solo lectura)
@app.route("/products")
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def index_product():
    products = Product.query.all()
    return render_template("productos/index_product.html", products=products)

# Ruta para agregar un nuevo producto (solo Gerente)
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@role_required("Gerente")
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category']
        created_at = datetime.now().date()

        # Crear un nuevo producto
        new_product = Product(
            name=name,
            price=price,
            stock=stock,
            FK_category=category_id,
            createdAt=created_at,
            updatedAt=created_at
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('index_product'))
    return render_template("productos/add_product.html", categories=categories)

# Ruta para editar un producto existente (solo Gerente)
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Gerente")
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.stock = request.form['stock']
        product.FK_category = request.form['category']
        product.updatedAt = datetime.now().date()
        db.session.commit()
        return redirect(url_for('index_product'))
    return render_template("productos/edit_product.html", product=product, categories=categories)

# Ruta para eliminar un producto (solo Gerente)
@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
@role_required("Gerente")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index_product'))

# Rutas para clientes (Empleado, Administrador, Gerente)
@app.route("/clients")
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def index_client():
    clients = Client.query.all()
    return render_template("clientes/index_client.html", clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def add_client():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        address = request.form['address']
        birth_date = request.form['birthDate']
        phone_number = request.form['phoneNumber']
        email = request.form['email']
        created_at = datetime.now().date()
        new_client = Client(
            firstName=first_name,
            lastName=last_name,
            address=address,
            birthDate=birth_date,
            phoneNumber=phone_number,
            email=email,
            createdAt=created_at,
            updatedAt=created_at
        )
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('index_client'))
    return render_template("clientes/add_client.html")

@app.route('/edit_client/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def edit_client(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.firstName = request.form['firstName']
        client.lastName = request.form['lastName']
        client.address = request.form['address']
        client.birthDate = request.form['birthDate']
        client.phoneNumber = request.form['phoneNumber']
        client.email = request.form['email']
        client.updatedAt = datetime.now().date()
        db.session.commit()
        return redirect(url_for('index_client'))
    return render_template("clientes/edit_client.html", client=client)

@app.route('/delete_client/<int:id>', methods=['POST'])
@login_required
@role_required("Gerente")
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('index_client'))

# Rutas para categorías (Administrador, Gerente)
@app.route("/categories")
@login_required
@role_required("Administrador", "Gerente")
def index_category():
    categories = Category.query.all()
    return render_template("categorias/index_category.html", categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
@login_required
@role_required("Gerente")
def add_category():
    if request.method == 'POST':
        category_name = request.form['categoryName']
        description = request.form['description']
        created_at = datetime.now().date()
        new_category = Category(
            cathegoryName=category_name,
            description=description,
            createdAt=created_at,
            updatedAt=created_at,
            state=True
        )
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('index_category'))
    return render_template("categorias/add_category.html")

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Gerente")
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.cathegoryName = request.form['categoryName']
        category.description = request.form['description']
        category.updatedAt = datetime.now().date()
        db.session.commit()
        return redirect(url_for('index_category'))
    return render_template("categorias/edit_category.html", category=category)

@app.route('/delete_category/<int:id>', methods=['POST'])
@login_required
@role_required("Gerente")
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('index_category'))
############# Rutas de Categorías ############
# Ruta para mostrar todos los detalles de ventas (Administrador, Gerente)
@app.route("/details")
@login_required
@role_required("Administrador", "Gerente")
def index_details():
    details = Detail.query.all()
    return render_template("details/index_details.html", details=details)

# Ruta para agregar un nuevo detalle de venta (Administrador, Gerente)
@app.route('/add_detail', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def add_detail():
    bills = Bill.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        FK_bill = request.form['FK_bill']
        FK_producto = request.form['FK_producto']
        created_at = datetime.now().date()
        updated_at = created_at
        state = True

        new_detail = Detail(
            FK_bill=FK_bill,
            FK_producto=FK_producto,
            createdAt=created_at,
            updatedAt=updated_at,
            state=state
        )

        db.session.add(new_detail)
        db.session.commit()
        return redirect(url_for('index_details'))
    return render_template('details/add_detail.html', bills=bills, products=products)

# Ruta para editar un detalle de venta existente (Administrador, Gerente)
@app.route('/edit_detail/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def edit_detail(id):
    detail = Detail.query.get_or_404(id)
    bills = Bill.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        detail.FK_bill = request.form['FK_bill']
        detail.FK_producto = request.form['FK_producto']
        detail.updatedAt = datetime.now().date()
        db.session.commit()
        return redirect(url_for('index_details'))
    return render_template('details/edit_detail.html', detail=detail, bills=bills, products=products)

# Ruta para eliminar un detalle de venta (Gerente)
@app.route('/delete_detail/<int:id>', methods=['POST'])
@login_required
@role_required("Gerente")
def delete_detail(id):
    detail = Detail.query.get_or_404(id)
    db.session.delete(detail)
    db.session.commit()
    return redirect(url_for('index_details'))
############# Rutas de Facturas #############

# Ruta para mostrar todas las facturas (Empleado, Administrador, Gerente)
@app.route("/bills")
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def index_bills():
    bills = Bill.query.all()  # Obtener todas las facturas
    return render_template("bills/index_bills.html", bills=bills)

# Ruta para agregar una nueva factura (Administrador, Gerente)
@app.route('/add_bill', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def add_bill():
    clients = Client.query.all()  # Obtener todos los clientes
    payment_methods = PaymentMethod.query.all()  # Obtener todos los métodos de pago

    if request.method == 'POST':
        FK_client = request.form['FK_client']
        FK_paymentMethod = request.form['FK_paymentMethod']
        created_at = datetime.now()
        updated_at = created_at
        state = True

        # Validar que los campos no estén vacíos y sean números
        if not FK_client or not FK_paymentMethod:
            return redirect(url_for('add_bill'))

        try:
            # Convertir a enteros
            FK_client = int(FK_client)
            FK_paymentMethod = int(FK_paymentMethod)
        except ValueError:
            return redirect(url_for('add_bill'))

        # Crear una nueva factura
        new_bill = Bill(
            FK_client=FK_client,
            FK_paymentMethod=FK_paymentMethod,
            createdAt=created_at,
            updatedAt=updated_at,
            state=state
        )

        # Agregar la factura a la base de datos
        db.session.add(new_bill)
        db.session.commit()

        return redirect(url_for('index_bills'))  # Redirige a la página de facturas

    return render_template('bills/add_bill.html', clients=clients, payment_methods=payment_methods)

# Ruta para editar una factura existente (Administrador, Gerente)
@app.route('/edit_bill/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def edit_bill(id):
    bill = Bill.query.get_or_404(id)
    clients = Client.query.all()  # Obtener todos los clientes
    payment_methods = PaymentMethod.query.all()  # Obtener todos los métodos de pago

    if request.method == 'POST':
        bill.FK_client = int(request.form['FK_client'])
        bill.FK_paymentMethod = int(request.form['FK_paymentMethod'])
        bill.updatedAt = datetime.now()  # Actualizamos la fecha de modificación

        db.session.commit()
        return redirect(url_for('index_bills'))  # Redirige a la página de facturas

    return render_template('bills/edit_bill.html', bill=bill, clients=clients, payment_methods=payment_methods)

# Ruta para ver una factura (Empleado, Administrador, Gerente)
@app.route("/bill/<int:id>")
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def bill(id):
    bill = Bill.query.get_or_404(id)  # Obtener la factura por ID
    details = Detail.query.filter_by(FK_bill=id).all()  # Obtener los detalles de la factura
    return render_template("bills/bill.html", bill=bill, details=details)

# Ruta para generar un PDF de la factura (Administrador, Gerente)
@app.route("/bill/<int:id>/pdf")
@login_required
@role_required("Administrador", "Gerente")
def bill_pdf(id):
    # Crear datos ficticios para demostrar
    bill = {
        "PK_bill": id,
        "client_name": "Juan Pérez",
        "payment_method": "Tarjeta de Crédito",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    details = [
        {"product_name": "Producto A", "quantity": 2, "unit_price": 50.00},
        {"product_name": "Producto B", "quantity": 1, "unit_price": 100.00},
    ]

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"Factura N° {bill['PK_bill']}", ln=True, align="C")

    # Información del cliente y factura
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, txt=f"Cliente: {bill['client_name']}")
    pdf.ln(8)
    pdf.cell(100, 10, txt=f"Método de Pago: {bill['payment_method']}")
    pdf.ln(8)
    pdf.cell(100, 10, txt=f"Fecha: {bill['date']}")

    # Calcular el total de la factura
    total_factura = sum(item["quantity"] * item["unit_price"] for item in details)
    pdf.ln(8)
    pdf.cell(100, 10, txt=f"Total: {total_factura:.2f} Bs")

    # Detalles de la factura
    pdf.ln(15)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(70, 10, txt="Producto", border=1, align="C")
    pdf.cell(30, 10, txt="Cantidad", border=1, align="C")
    pdf.cell(40, 10, txt="Precio Unitario", border=1, align="C")
    pdf.cell(50, 10, txt="Total", border=1, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for item in details:
        total_item = item["quantity"] * item["unit_price"]
        pdf.cell(70, 10, txt=item["product_name"], border=1)
        pdf.cell(30, 10, txt=str(item["quantity"]), border=1, align="C")
        pdf.cell(40, 10, txt=f"{item['unit_price']:.2f} Bs", border=1, align="C")
        pdf.cell(50, 10, txt=f"{total_item:.2f} Bs", border=1, align="C")
        pdf.ln(10)

    # Guardar el PDF en memoria
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest="S").encode("latin1"))
    pdf_output.seek(0)

    # Enviar el PDF como respuesta
    return send_file(
        pdf_output,
        download_name=f"factura_{bill['PK_bill']}.pdf",  # Cambiado a download_name
        as_attachment=True,
    )

 ############# Rutas de Métodos de Pago #############

# Ruta para mostrar todos los métodos de pago (Empleado, Administrador, Gerente)
@app.route("/payment_methods")
@login_required
@role_required("Empleado", "Administrador", "Gerente")
def index_payment_methods():
    payment_methods = PaymentMethod.query.all()  # Obtener todos los métodos de pago
    return render_template("payment_methods/index_payment_methods.html", payment_methods=payment_methods)

# Ruta para agregar un nuevo método de pago (Administrador, Gerente)
@app.route('/add_payment_method', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def add_payment_method():
    if request.method == 'POST':
        name = request.form['name']
        anotherDetails = request.form['anotherDetails']
        created_at = datetime.now().date()
        updated_at = created_at
        state = True

        # Crear un nuevo método de pago
        new_payment_method = PaymentMethod(
            name=name,
            anotherDetails=anotherDetails,
            createdAt=created_at,
            updatedAt=updated_at,
            state=state
        )

        # Agregar el método de pago a la base de datos
        db.session.add(new_payment_method)
        db.session.commit()

        return redirect(url_for('index_payment_methods'))  # Redirige a la página de métodos de pago

    return render_template('payment_methods/add_payment_method.html')

# Ruta para editar un método de pago existente (Administrador, Gerente)
@app.route('/edit_payment_method/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required("Administrador", "Gerente")
def edit_payment_method(id):
    payment_method = PaymentMethod.query.get_or_404(id)

    if request.method == 'POST':
        payment_method.name = request.form['name']
        payment_method.anotherDetails = request.form['anotherDetails']
        payment_method.updatedAt = datetime.now().date()

        # Actualizar el método de pago en la base de datos
        db.session.commit()

        return redirect(url_for('index_payment_methods'))  # Redirige a la página de métodos de pago

    return render_template('payment_methods/edit_payment_method.html', payment_method=payment_method)

# Ruta para eliminar un método de pago (Administrador, Gerente)
@app.route('/delete_payment_method/<int:id>', methods=['POST'])
@login_required
@role_required("Administrador", "Gerente")
def delete_payment_method(id):
    payment_method = PaymentMethod.query.get_or_404(id)
    db.session.delete(payment_method)
    db.session.commit()
    return redirect(url_for('index_payment_methods'))  # Redirige a la página de métodos de pago


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)