from extensions import db


class Rider(db.Model):
    __tablename__ = "riders"

    rider_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rider_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)