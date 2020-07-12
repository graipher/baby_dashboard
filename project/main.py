from flask import Blueprint, render_template, request, redirect, url_for, flash
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


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, children=current_user.children)


@main.route('/profile', methods=["POST"])
@login_required
def profile_post():
    name = request.form.get('name')
    date = pd.to_datetime(request.form.get('date'), errors="raise")
    gender = request.form.get('gender')
    color = request.form.get('color')
    new_child = Child(name=name, birth_date=date,
                      gender=gender.lower(), color=color)
    current_user.children.append(new_child)
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route('/plots')
@login_required
def plots():
    plots = "weight", "height"
    return render_template('plots.html', plots=plots, resources=CDN.render())


@main.route('/plots/<y>')
@login_required
def plot(y):
    name = request.args.get("name")
    file_name = request.args.get("file_name")
    if name and file_name:
        df = pd.read_csv(request.args.get("file_name"))
        df["Date"] = pd.to_datetime(df["Date"])
        child = current_user.children.filter_by(name=name).one()
        child.measurements.extend(
            [Measurement(m_type=y, *t[1:]) for t in df.itertuples()])
        db.session.commit()
    return render_template('plot.html', plot=y, resources=CDN.render(), children=current_user.children)


@main.route('/plots/<y>', methods=["POST"])
@login_required
def plot_post(y):
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
    ref = get_reference_data(y)
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
    title = {"weight": "Weight [g]",
             "height": "Height [cm]"}
    p = setup_figure("Date", title[y])
    for child in current_user.children:
        line_plot(p, y, child)
    reference(p, y)
    p.legend.location = "top_left"
    return json.dumps(json_item(p, y))


# @main.route('/plots/weight')
# @login_required
# def plot_weight():
#     #ds = get_data("weight")
#     p = setup_figure("Date", "Weight [g]")
#     for child in current_user.children:
#         ds = child.get_data("weight")
#         p.circle(
#             x="Date", y="weight", size=10, color=child.color, source=ds, legend_label=child.name
#         )
#         p.line(
#             x="Date",
#             y="weight",
#             color=child.color,
#             line_width=3,
#             line_dash="dashed",
#             source=ds,
#         )
#     # hline = Span(
#     #     location=0.9 * ds.data["Weight"][0],
#     #     dimension="width",
#     #     line_color="gray",
#     #     line_width=3,
#     #     line_dash="dotted",
#     # )
#     # p.renderers.append(hline)
#     # t = Label(x=0.5, x_units="screen", y=0.9 *
#     #           ds.data["Weight"][0], text="-10%")
#     # p.add_layout(t)
#     p.legend.location = "top_left"
#     ref = get_reference_data("weight")
#     p.line(
#         x="Date", y="P50", color="gray", line_width=2, legend_label="Median", source=ref
#     )
#     p.line(x="Date", y="P1", color="gray",
#            line_width=1, line_dash="dotted", source=ref)
#     p.line(
#         x="Date", y="P5", color="gray", line_width=1, line_dash="dotdash", source=ref
#     )
#     p.line(
#         x="Date", y="P10", color="gray", line_width=1, line_dash="dashed", source=ref
#     )
#     p.line(
#         x="Date",
#         y="P90",
#         color="gray",
#         line_width=1,
#         line_dash="dashed",
#         legend_label="90%",
#         source=ref,
#     )
#     p.line(
#         x="Date",
#         y="P95",
#         color="gray",
#         line_width=1,
#         line_dash="dotdash",
#         legend_label="95%",
#         source=ref,
#     )
#     p.line(
#         x="Date",
#         y="P99",
#         color="gray",
#         line_width=1,
#         line_dash="dotted",
#         legend_label="99%",
#         source=ref,
#     )
#     return json.dumps(json_item(p, "weight"))


# @main.route('/plots/height')
# @login_required
# def plot_height():
#     ds = get_data("height")
#     print(ds.data)
#     p = setup_figure("Date", "Height [cm]")
#     p.circle(
#         x="Date", y="Height", size=10, color=colors[0], legend_label=current_user.children[0].name, source=ds
#     )
#     p.line(
#         x="Date",
#         y="Height",
#         color=colors[0],
#         line_width=3,
#         line_dash="dashed",
#         source=ds,
#     )
#     p.legend.location = "top_left"
#
#
#     return json.dumps(json_item(p, "height"))
