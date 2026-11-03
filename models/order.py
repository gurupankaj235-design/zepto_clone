from extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cust_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    order_val = db.Column(db.Float, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False)
    order_status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending"
    )