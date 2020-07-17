from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import db
from .models import User, Child, Measurement
from .plots import setup_figure, get_data, get_reference_data, colors
import json
from bokeh.embed import json_item
from bokeh.models import Span, Label, ColumnDataSource
from bokeh.resources import CDN
import pandas as pd

from datetime import datetime

main = Blueprint('main', __name__)

PLOTS = {"weight": "Weight [g]",
         "height": "Height [cm]",
         "sleep": "Time [h]",
         "amount": "Amount [ml]"}


@main.route('/')
def index():
    return render_template('index.html', plots=PLOTS)


@main.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404', plots=PLOTS), 404


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, children=current_user.children, plots=PLOTS)


@main.route('/profile', methods=["POST"])
@login_required
def profile_post():
    name = request.form.get('name')
    date = pd.to_datetime(request.form.get('date'), errors="raise")
    gender = request.form.get('gender').lower()
    color = request.form.get('color')
    new_child = Child(name=name, birth_date=date,
                      gender=gender, color=color)
    current_user.children.append(new_child)
    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/profile/edit/<id>')
@login_required
def profile_edit(id):
    try:
        child = current_user.children.filter_by(id=id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)
    return render_template('profile_edit.html', child=child, plots=PLOTS)

@main.route('/profile/edit/<id>', methods=["POST"])
@login_required
def profile_edit_post(id):
    try:
        child = current_user.children.filter_by(id=id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)
    child.name = request.form.get('name')
    child.birth_date = pd.to_datetime(request.form.get('date'), errors="raise")
    child.gender = request.form.get('gender').lower()
    child.color = request.form.get('color')
    print(child)
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route('/plots')
@login_required
def plots():
    return render_template('plots.html', plots=PLOTS, resources=CDN.render())


@main.route('/plots/<y>')
@login_required
def plot(y):
    if y not in PLOTS:
        abort(404)
    name = request.args.get("name")
    file_name = request.args.get("file_name")
    if name and file_name:
        df = pd.read_csv(request.args.get("file_name"))
        df["Date"] = pd.to_datetime(df["Date"])
        child = current_user.children.filter_by(name=name).one()
        print(df)
        child.measurements.extend(
            [Measurement(m_type=y, date=t[1], value=t[2]) for t in df.itertuples()])
        db.session.commit()
    return render_template('plot.html', plot=y, resources=CDN.render(), children=current_user.children, plots=PLOTS)


@main.route('/plots/<y>', methods=["POST"])
@login_required
def plot_post(y):
    if y not in PLOTS:
        abort(404)
    try:
        date = pd.to_datetime(request.form.get('date'), errors="raise")
        value = float(request.form.get('value'))
        child_name = request.form.get('child')
        child = current_user.children.filter_by(name=child_name).one()
    except ValueError:
        flash('Please enter a date and a number')
    else:
        child.measurements.append(Measurement(
            m_type=y, date=date, value=value))
        db.session.commit()
    return redirect(url_for('main.plot', y=y))


def line_plot(p, y, child):
    ds = child.get_data(y)
    p.circle(x="date", y=y, size=10, color=child.color,
             source=ds, legend_label=child.name)
    p.line(x="date", y=y, color=child.color,
           line_width=3, line_dash="dashed", source=ds)


def reference(p, y):
    try:
        ref = get_reference_data(y)
    except FileNotFoundError:
        return
    options = dict(x="Date", color="gray", source=ref)
    p.line(y="P50", line_width=2, legend_label="Median", **options)
    p.line(y="P5", line_width=1, line_dash="dotted", **options)
    p.line(y="P10", line_width=1, line_dash="dashed", **options)
    p.line(y="P90", line_width=1, line_dash="dashed",
           legend_label="90%", **options)
    p.line(y="P95", line_width=1, line_dash="dotted",
           legend_label="95%", **options)


@main.route('/bokeh/<y>')
@login_required
def plot_bokeh(y):
    if y not in PLOTS:
        abort(404)
    p = setup_figure("Date", PLOTS[y])
    for child in current_user.children:
        line_plot(p, y, child)
    reference(p, y)
    p.legend.location = "top_left"
    return json.dumps(json_item(p, y))
