
import os

from flask import Flask, request, jsonify 
from dotenv import load_dotenv
from extensions import db
from models.customer import Customer
from models.product import Product
from models.inventory import Inventory
from models.order import Order
from models.rider import Rider
from models.delivery import Delivery
from flask_jwt_extended import JWTManager
from models.user import User
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

jwt  = JWTManager(app)
CORS(app)


with app.app_context():
    db.create_all()


# Endpoint 3: Get All Customers API
@app.route("/customers" , methods=["GET"])
@jwt_required() 
def get_customers():

    user_id = get_jwt_identity()

    customers = Customer.query.all()

    return jsonify([
        {"cust_id": customer.cust_id,
         "customer_name": customer.customer_name,
         "phone":customer.phone,
         "city": customer.city}
         for customer in customers])



# Endpoint 4: Update Customer API
@app.route("/customers/<int:id>", methods = ["PUT"])
@jwt_required() 
def update_customer(id):
    customer = db.session.get(Customer, id)
    if customer is None:
        return jsonify({"error":"Customer not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    customer.customer_name = data.get("customer_name", customer.customer_name)
    customer.phone = data.get("phone", customer.phone)
    customer.city = data.get("city", customer.city)

    db.session.commit()

    return jsonify({"message": "Customer updated successfully",
                    "customer": {"cust_id": customer.cust_id,
                                 "customer_name": customer.customer_name,
                                 "phone": customer.phone,
                                 "city": customer.city}}), 200

    

    


# Endpoint 5: Create Customer API
@app.route("/customers", methods = ["POST"])
@jwt_required() 
def create_customers():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    required_fields = ["customer_name", "phone", "city"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400 

    phone = data["phone"]

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"error": "Phone number must be exactly 10 digits"}), 400
        
    existing_customer = Customer.query.filter_by(phone = data["phone"]).first()
    if existing_customer:
        return jsonify({"error": "Phone number already registered"}),409

    new_customer = Customer(
        customer_name = data["customer_name"],
        phone = data["phone"],
        email = data.get("email"),
        city = data["city"],
        gender=data.get("gender"),
        pincode=data.get("pincode"))

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({
        "message": "Customer created successfully",
         "customer": {
             "cust_id": new_customer.cust_id,
             "customer_name": new_customer.customer_name,
             "phone": new_customer.phone,
             "email": new_customer.email,
             "city": new_customer.city}}), 201





# Endpoint 6: Get Customer by ID API
@app.route("/customers/<int:id>", methods=["GET"])
@jwt_required() 
def get_customer(id):
    customer = db.session.get(Customer,id)

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"customer": {"cust_id": customer.cust_id,
                                 "customer_name": customer.customer_name,
                                 "phone": customer.phone,
                                 "email": customer.email,
                                 "city": customer.city}}),200
                                 
                                 
                                



# Endpoint 2: Database Connection Check API
@app.route("/db_check", methods=["GET"])
def db_check():
    try:
        with db.engine.connect() as connection:
            return jsonify({"message": "Database connected successfully"})
    except Exception as error:
        return jsonify({"message": "Database connection failed",
                        "error": str(error)}), 500


# Endpoint 1: Home API
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Zepto Clone API",
        "status": "successful"})


# Endpoint 7: Delete Customer API
@app.route("/customers/<int:id>", methods=["DELETE"])
@jwt_required() 
def delete_customer(id):
    customer = db.session.get(Customer,id)

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404
    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully"}), 200



# Endpoint 8: Get All Products
@app.route("/products", methods=["GET"])
@jwt_required() 
def get_products():
    products = Product.query.all()

    return jsonify([
        {"product_id": product.product_id,
         "prod_name": product.prod_name,
         "price": float(product.price),
         "category": product.category}

         for product in products])



# Endpoint 9: Get Product by ID
@app.route("/products/<int:id>", methods = ["GET"])
@jwt_required() 
def get_product_by_id(id):
    product = db.session.get(Product, id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"product_id": product.product_id,
                    "prod_name":product.prod_name,
                    "price": float(product.price),
                    "category": product.category}), 200



# Endpoint 10: Create Product
@app.route("/products", methods=["POST"])
@jwt_required()
def create_product():

    data = request.get_json()
    if not data:
        return jsonify({"error": "json body is required"}), 400

    required_fields = ["prod_name", "price"]

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            return jsonify({"error": f"{field} is required"}), 400

    # Validate product price
    price = data["price"]

    if type(price) not in (int, float) or price <= 0:
        return jsonify({
            "error": "price must be a positive number"}), 400

    if Product.query.filter_by(prod_name=data["prod_name"]).first():
        return jsonify({"error": "Product already exists"}), 409

    product = Product(
        prod_name=data["prod_name"],
        price=price,
        category=data.get("category"))

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": {
            "product_id": product.product_id,
            "prod_name": product.prod_name,
            "price": float(product.price),
            "category": product.category}}), 201


# Endpoint 11: Update Product
@app.route("/products/<int:id>", methods=["PUT"])
@jwt_required()
def update_product(id):
    product = db.session.get(Product, id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    if "prod_name" in data:
        new_name = data["prod_name"]

        if not isinstance(new_name, str) or not new_name.strip():
            return jsonify({"error": "prod_name cannot be empty"}), 400

        existing_product = Product.query.filter_by(prod_name=new_name).first()

        if existing_product and existing_product.product_id != id:
            return jsonify({"error": "Product already exists"}), 409

        product.prod_name = new_name

    if "price" in data:

        new_price = data["price"]

        if type(new_price) not in (int, float) or new_price <= 0:
            return jsonify({"error": "price must be a positive number"}), 400

        product.price = new_price

    if "category" in data:
        product.category = data["category"]

    db.session.commit()
    return jsonify({
        "message": "Product updated successfully",
        "product": {
            "product_id": product.product_id,
            "prod_name": product.prod_name,
            "price": float(product.price),
            "category": product.category}}), 200


# Endpoint 12: Delete Product API
@app.route("/products/<int:id>", methods=["DELETE"])
@jwt_required() 
def delete_product(id):
    product = db.session.get(Product,id)

    if product is None:
        return jsonify({"error":"product is not found"}), 404
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted successfully"}), 200
    




# Endpoint 13: Get All Inventory
@app.route("/inventory", methods = ["GET"])
@jwt_required() 
def get_inventory():
    inventories = Inventory.query.all()

    return jsonify({"inventory": [{"product_id": item.product_id,
                                   "quantity_in_stock": item.quantity_in_stock}
                                   for item in inventories]}), 200





# Endpoint 14: Retrieve all inventory records
@app.route("/inventory/<int:id>", methods=["GET"])
@jwt_required() 
def get_inventory_by_id(id):

    inventory = db.session.get(Inventory, id)

    if inventory is None:
        return jsonify({"message":"Item not found"}), 404

    return jsonify({"inventory": {"product_id": inventory.product_id,
                                  "quantity_in_stock": inventory.quantity_in_stock}}),200




# Endpoint 15: Create initial inventory for an existing product
@app.route("/inventory/<int:id>", methods=["POST"])
@jwt_required() 
def add_inventory(id):

    product = db.session.get(Product, id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    inventory = db.session.get(Inventory, id)

    if inventory is not None:
        return jsonify({
            "error": "Inventory record already exists. Use PATCH to add stock."}), 409

    data = request.get_json()

    if not data or "quantity" not in data:
        return jsonify({"error": "quantity is required"}), 400

    quantity = data["quantity"]

    if type(quantity) != int or quantity <= 0:
        return jsonify({
            "error": "quantity must be a positive integer"}), 400

    inventory = Inventory(
        product_id=id,
        quantity_in_stock=quantity)

    db.session.add(inventory)
    db.session.commit()

    return jsonify({
        "message": "Initial inventory created successfully",
        "inventory": {
            "product_id": inventory.product_id,
            "quantity_in_stock": inventory.quantity_in_stock}}), 201




# Endpoint 16:  Add quantity to existing inventory
@app.route("/inventory/<int:id>", methods=["PATCH"])
@jwt_required() 
def update_inventory(id):
    inventory = db.session.get(Inventory, id)

    if inventory is None:
        return jsonify({"error": "Inventory not found"}), 404

    data = request.get_json()

    if not data or "quantity" not in data:
        return jsonify({"error": "quantity is required"}), 400

    quantity = data["quantity"]

    if type(quantity) != int or quantity <= 0:
        return jsonify({"error": "quantity must be a positive integer"}) ,400

    inventory.quantity_in_stock += quantity
    db.session.commit()
    return jsonify({"message": "Stock added successfully",
                    "inventory": {"product_id": inventory.product_id,
                                  "quantity_in_stock": inventory.quantity_in_stock}}), 200







# Endpoint 17: GET API: Fetch all orders with product name
@app.route("/orders", methods=["GET"])
@jwt_required() 
def get_orders():
    orders = db.session.query(
        Order, Product.prod_name
    ).join(
        Product, Order.product_id == Product.product_id
    ).all()
    return jsonify({
        "orders": [{
                "order_id": order.order_id,
                "cust_id": order.cust_id,
                "product_id": order.product_id,
                "product_name": product_name,
                "order_val": order.order_val,
                "quantity": order.quantity,
                "order_status": order.order_status}
            for order, product_name in orders]}), 200


# Endpoint 18: GET API: Fetch a single order by ID with product name
@app.route("/orders/<int:id>", methods=["GET"])
@jwt_required() 
def get_order_by_id(id):
    result = db.session.query(
        Order, Product.prod_name
    ).join(
        Product, Order.product_id == Product.product_id
    ).filter(
        Order.order_id == id
    ).first()
    if result is None:
        return jsonify({"error": "Order not found"}), 404

    order, product_name = result

    return jsonify({
        "order": {
            "order_id": order.order_id,
            "cust_id": order.cust_id,
            "product_id": order.product_id,
            "product_name": product_name,
            "order_val": order.order_val,
            "quantity": order.quantity,
            "order_status": order.order_status}}), 200




# Endpoint 19: POST API: Create a new order
@app.route("/orders", methods=["POST"])
@jwt_required() 
def create_order():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

        
    if "cust_id" not in data:
        return jsonify({"error": "cust_id is required"}), 400

    
    customer = db.session.get(Customer, data["cust_id"])

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

        
    if "product_id" not in data:
        return jsonify({"error": "product_id is required"}), 400

    
    product = db.session.get(Product, data["product_id"])

    if product is None:
        return jsonify({"error": "Product not found"}), 404

        
    if "quantity" not in data:
        return jsonify({"error": "quantity is required"}), 400

    quantity = data["quantity"]

    if type(quantity) != int or quantity <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400

        
    inventory = db.session.get(Inventory, data["product_id"])

    if inventory is None:
        return jsonify({"error": "Inventory record not found"}), 404

    
    if inventory.quantity_in_stock < quantity:
        return jsonify({
            "error": "Insufficient stock",
            "available_stock": inventory.quantity_in_stock
        }), 400

        # Calculate total order value
    order_val = float(product.price) * quantity

        # Create a new order object
    new_order = Order(
        cust_id=customer.cust_id,
        product_id=product.product_id,
        order_val=order_val,
        quantity=quantity,
        order_status="Confirmed")

        # Deduct ordered quantity from inventory
    inventory.quantity_in_stock -= quantity

        
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order created successfully",
                    "order": {"order_id": new_order.order_id,
                    "cust_id": customer.cust_id,
                    "customer_name": customer.customer_name,
                    "product_id": product.product_id,
                    "product_name": product.prod_name,
                    "price": float(product.price),
                    "quantity": quantity,
                    "order_val": order_val,
                    "order_status": new_order.order_status}}), 201



# Endpoint 20: Cancel Order API
@app.route("/orders/<int:id>/cancel", methods=["PATCH"])
@jwt_required() 
def cancel_order(id):
    order = db.session.get(Order, id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    if order.order_status != "Confirmed":
        return jsonify({
            "error": "Only confirmed orders can be cancelled"}), 400

    inventory = db.session.get(Inventory, order.product_id)

    if inventory is None:
        return jsonify({"error": "Inventory record not found"}), 404

    inventory.quantity_in_stock += order.quantity

    order.order_status = "Cancelled"

    db.session.commit()

    return jsonify({
        "message": "Order cancelled successfully",

        "order": {
            "order_id": order.order_id,
            "order_status": order.order_status},

        "inventory": {
            "product_id": inventory.product_id,
            "quantity_in_stock": inventory.quantity_in_stock}}), 200




# Endpoint 21: Get All Riders
@app.route("/riders", methods=["GET"])
@jwt_required() 
def get_riders():
    riders = Rider.query.all()

    return jsonify({
        "riders": [
            {
            "rider_id": rider.rider_id,
            "rider_name": rider.rider_name,
            "phone": rider.phone,
            "city": rider.city,
            "email": rider.email}
            for rider in riders]}), 200




# Endpoint 22: Get All Assigned Riders
@app.route("/riders/assigned", methods=["GET"])
@jwt_required() 
def get_assigned_riders():
    assigned_riders = db.session.query(Rider, Delivery).join(Delivery, Rider.rider_id == Delivery.rider_id).all()
    return jsonify({"assigned_riders": [
        {"rider_id": rider.rider_id,
         "rider_name": rider.rider_name,
         "phone": rider.phone,
         "city": rider.city,
         "email": rider.email,
         "delivery_id": delivery.delivery_id,
         "order_id": delivery.order_id,
         "cust_id": delivery.cust_id,
         "delivery_status": delivery.delivery_status,
         "payment_status": delivery.payment_status}
         for rider, delivery in assigned_riders
    ]}),200









# Endpoint 23: Get Rider by ID
@app.route("/riders/<int:id>", methods=["GET"])
@jwt_required() 
def get_rider_by_id(id):
    rider = db.session.get(Rider, id)
    if rider is None:
        return jsonify({"error": "Rider not found"}), 404

    return jsonify({"rider": {
                "rider_id": rider.rider_id,
                "rider_name": rider.rider_name,
                "phone": rider.phone,
                "city": rider.city,
                "email": rider.email}}), 200




# Endpoint 24: Assign Rider to Order
@app.route("/deliveries", methods=["POST"])
@jwt_required() 
def assign_rider():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    if "order_id" not in data or "rider_id" not in data:
        return jsonify({"error": "order_id and rider_id are required"}), 400

    order_id = data["order_id"]
    rider_id = data["rider_id"]

    if type(order_id) != int or order_id <= 0:
        return jsonify({"error": "order_id must be a positive integer"}), 400

    if type(rider_id) != int or rider_id <= 0:
        return jsonify({"error": "rider_id must be a positive integer"}), 400

    order = db.session.get(Order, order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    rider = db.session.get(Rider, rider_id)

    if rider is None:
        return jsonify({"error": "Rider not found"}), 404

    if order.order_status != "Confirmed":
        return jsonify({"error": "Only confirmed orders can be assigned"}), 400

    existing_delivery = Delivery.query.filter_by(order_id=order_id).first()

    if existing_delivery:
        return jsonify({"error": "Rider is already assigned to this order"}), 409

    new_delivery = Delivery(
        rider_id=rider_id,
        cust_id=order.cust_id,
        order_id=order_id,
        delivery_status="Pending",
        payment_status="Pending")

    order.order_status = "Assigned"

    db.session.add(new_delivery)
    db.session.commit()

    return jsonify({
        "message": "Rider assigned successfully",
        "delivery": {
            "delivery_id": new_delivery.delivery_id,
            "rider_id": rider.rider_id,
            "rider_name": rider.rider_name,
            "order_id": order.order_id,
            "cust_id": order.cust_id,
            "delivery_status": new_delivery.delivery_status,
            "payment_status": new_delivery.payment_status}}), 201





# Endpoint 25: Update Delivery Status
@app.route("/deliveries/<int:id>/status", methods=["PATCH"])
@jwt_required() 
def update_delivery_status(id):

    delivery = db.session.get(Delivery, id)

    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404

    data = request.get_json()

    if not data or "delivery_status" not in data:
        return jsonify({"error": "delivery_status is required"}), 400

    new_status = data["delivery_status"]

    allowed_statuses = ["Picked Up", "In Transit", "Delivered"]

    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid delivery status"}), 400

    delivery.delivery_status = new_status

    if new_status == "Delivered":
        order = db.session.get(Order, delivery.order_id)
        order.order_status = "Delivered"

    db.session.commit()

    return jsonify({
        "message": "Delivery status updated successfully",
        "delivery": {
            "delivery_id": delivery.delivery_id,
            "order_id": delivery.order_id,
            "delivery_status": delivery.delivery_status}}), 200




# Endpoint 26: Get All Deliveries
@app.route("/deliveries", methods=["GET"])
@jwt_required() 
def get_deliveries():

    deliveries = Delivery.query.all()

    return jsonify({
        "deliveries": [
            
            {"delivery_id": delivery.delivery_id,
            "rider_id": delivery.rider_id,
            "cust_id": delivery.cust_id,
            "order_id": delivery.order_id,
            "delivery_status": delivery.delivery_status,
            "payment_status": delivery.payment_status}
            for delivery in deliveries]}), 200





# Endpoint 27: Get Delivery by ID
@app.route("/deliveries/<int:id>", methods=["GET"])
@jwt_required() 
def get_delivery_by_id(id):

    delivery = db.session.get(Delivery, id)

    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404

    return jsonify({
        "delivery": {
            "delivery_id": delivery.delivery_id,
            "rider_id": delivery.rider_id,
            "cust_id": delivery.cust_id,
            "order_id": delivery.order_id,
            "delivery_status": delivery.delivery_status,
            "payment_status": delivery.payment_status}}), 200





# Endpoint 28: Update Payment Status
@app.route("/deliveries/<int:id>/payment_status", methods=["PATCH"])
@jwt_required()
def update_payment_status(id):

    delivery = db.session.get(Delivery, id)
    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404

    data = request.get_json()
    if not data or "payment_status" not in data:
        return jsonify({"error": "payment_status is required"}), 400

    new_status = data["payment_status"]

    allowed_statuses = ["Pending", "Paid"]

    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid payment status"}), 400

    # Payment can be marked Paid only after delivery is completed
    if new_status == "Paid" and delivery.delivery_status != "Delivered":
        return jsonify({
            "error": "Payment can be marked Paid only after delivery is completed"}), 400

    delivery.payment_status = new_status

    db.session.commit()

    return jsonify({
        "message": "Payment status updated successfully",
        "delivery": {
            "delivery_id": delivery.delivery_id,
            "order_id": delivery.order_id,
            "payment_status": delivery.payment_status}}), 200







# API: Register a new user
@app.route("/register", methods = ["POST"])
def register_user():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error":"Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    existing_user = User.query.filter_by(email = email).first()

    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    password_hash = generate_password_hash(password)

    new_user = User(email = email, password_hash = password_hash)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully",
                    "user": {
                        "user_id": new_user.user_id,
                        "email": new_user.email,
                        "role": new_user.role}}), 201




# API: Login user
@app.route("/login", methods=["POST"])
def login_user():

    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity = str(user.user_id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role}}), 200





if __name__ == "__main__":
    app.run(debug=True)
