
from extensions import db


class Product(db.Model):
    __tablename__ = "zepto_products"

    product_id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.String(200), unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100))
