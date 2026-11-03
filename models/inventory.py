from extensions import db

class Inventory(db.Model):
    __tablename__ = "inventory"

    product_id = db.Column(db.Integer, primary_key=True)
    quantity_in_stock = db.Column(db.Integer, nullable=False)