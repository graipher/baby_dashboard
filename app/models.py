from functools import wraps
from flask_login import UserMixin
import enum
from bokeh.models import ColumnDataSource
from . import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    password = db.Column(db.String(100))
    children = db.relationship("Child", cascade="all,delete", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Gender(enum.Enum):
    male = 1
    female = 2
    other = 3

class Child(db.Model):
    __tablename__ = "children"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    birth_date = db.Column(db.DateTime)
    gender = db.Column(db.Enum(Gender))
    color = db.Column(db.String(7))
    measurements = db.relationship(
        "Measurement", cascade="all,delete", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Child(id={self.id}, name={self.name}, birth_date={self.birth_date}, gender={self.gender}, color={self.color})"

    def get_data(self, m_type):
        try:
            date, values = zip(*[(x.date, x.value)
                                 for x in self.measurements.filter_by(m_type=m_type)])
        except ValueError:
            date, values = [], []
        return ColumnDataSource({"date": date, m_type: values})


class Measurement(db.Model):
    __tablename__ = "measurement"
    id = db.Column(db.Integer, primary_key=True)
    m_type = db.Column(db.String(20))
    #unit = db.Column(db.String(20))
    date = db.Column(db.DateTime)
    value = db.Column(db.Float)
    value2 = db.Column(db.Float, nullable=True)
    value3 = db.Column(db.Float, nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey(
        "children.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<Measurement(m_type={self.m_type}, value={self.value})"
