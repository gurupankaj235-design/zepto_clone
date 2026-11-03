from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    cust_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    pincode = db.Column(db.String(10))