from extensions import db


class Delivery(db.Model):
    __tablename__ = "deliveries"

    delivery_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    rider_id = db.Column(db.Integer, nullable=False)
    cust_id = db.Column(db.Integer, nullable=False)
    delivery_status = db.Column(db.String(50),nullable=False,default="Pending")
    order_id = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(50),nullable=False,default="Pending")