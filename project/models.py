from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    weight = db.relationship("Weight", cascade="all,delete")
    height = db.relationship("Height", cascade="all,delete")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Weight(db.Model):
    __tablename__ = "weight"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    weight = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Weight(id={self.id}, date={self.date}, weight={self.weight})>"


class Height(db.Model):
    __tablename__ = "height"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    height = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Height(id={self.id}, date={self.date}, weight={self.height})>"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    measurements = db.relationship("Measurement", cascade="all,delete")
    # weight = db.relationship("Measurement",
    #                          cascade="all,delete",
    #                          primaryjoin="foreign(Measurement.measurement_type_id) == 0")
    # height = db.relationship("Height", cascade="all,delete")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Measurement(db.Model):
    __tablename__ = "measurement"
    id = db.Column(db.Integer, primary_key=True)
    m_type = db.Column(db.String(20))
    unit = db.Column(db.String(20))
    date = db.Column(db.DateTime)
    value = db.Column(db.Float)
    value2 = db.Column(db.Float, nullable=True)
    value3 = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Measurement(m_type={self.m_type}, value={self.value}, unit={self.unit})"
#
#
# class MeasurementType(db.Model):
#     __tablename__ = "measurement_type"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     unit = db.Column(db.String(100), nullable=True)
