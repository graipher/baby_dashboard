from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Weight, Height
from .plots import setup_figure, get_data, get_reference_data, colors
import json
from bokeh.embed import json_item
from bokeh.models import Span, Label
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
    print(Weight.query.filter(Weight.weight > 7000).all())
    return render_template('profile.html', name=current_user.name)

@main.route('/test/<plot>')
@login_required
def test(plot):
    print(plot)
    print([(x.date, x.weight) for x in current_user.weight])
    print(current_user.height)

@main.route('/weight')
@login_required
def weight():
    if request.args.get("file_name"):
        df = pd.read_csv(request.args.get("file_name"))
        df["Date"] = pd.to_datetime(df["Date"])
        current_user.weight.extend([
            Weight(date=row.Date, weight=row.Weight)
            for _, row in df.iterrows()
        ])
        db.session.commit()
    return render_template('plot.html', plot="weight", resources=CDN.render())

@main.route('/weight', methods=["POST"])
@login_required
def weight_post():
    try:
        date = pd.to_datetime(request.form.get('date'),errors="raise" )
        weight = float(request.form.get('weight'))
    except ValueError:
        flash('Please enter a date and a number')
    else:
        current_user.weight.append(Weight(date=date, weight=weight))
        db.session.commit()
    return redirect(url_for('main.weight'))

@main.route('/plots/weight')
@login_required
def plot_weight():
    ds = get_data("weight")
    p = setup_figure("Date", "Weight [g]")
    p.circle(
        x="Date", y="Weight", size=10, color=colors[0], source=ds, legend_label=current_user.name
    )
    p.line(
        x="Date",
        y="Weight",
        color=colors[0],
        line_width=3,
        line_dash="dashed",
        source=ds,
    )
    hline = Span(
        location=0.9 * ds.data["Weight"][0],
        dimension="width",
        line_color="gray",
        line_width=3,
        line_dash="dotted",
    )
    p.renderers.append(hline)
    t = Label(x=0.5, x_units="screen", y=0.9 * ds.data["Weight"][0], text="-10%")
    p.add_layout(t)
    p.legend.location = "top_left"
    ref = get_reference_data("weight")
    p.line(
        x="Date", y="P50", color="gray", line_width=2, legend_label="Median", source=ref
    )
    p.line(x="Date", y="P1", color="gray", line_width=1, line_dash="dotted", source=ref)
    p.line(
        x="Date", y="P5", color="gray", line_width=1, line_dash="dotdash", source=ref
    )
    p.line(
        x="Date", y="P10", color="gray", line_width=1, line_dash="dashed", source=ref
    )
    p.line(
        x="Date",
        y="P90",
        color="gray",
        line_width=1,
        line_dash="dashed",
        legend_label="90%",
        source=ref,
    )
    p.line(
        x="Date",
        y="P95",
        color="gray",
        line_width=1,
        line_dash="dotdash",
        legend_label="95%",
        source=ref,
    )
    p.line(
        x="Date",
        y="P99",
        color="gray",
        line_width=1,
        line_dash="dotted",
        legend_label="99%",
        source=ref,
    )
    return json.dumps(json_item(p, "weight"))

@main.route('/height')
@login_required
def height():
    if request.args.get("file_name"):
        df = pd.read_csv(request.args.get("file_name"))
        df["Date"] = pd.to_datetime(df["Date"])
        current_user.height.extend([
            Height(date=row.Date, height=row.Height)
            for _, row in df.iterrows()
        ])
        db.session.commit()
    return render_template('plot.html', plot="height", resources=CDN.render())

@main.route('/height', methods=["POST"])
@login_required
def height_post():
    try:
        date = pd.to_datetime(request.form.get('date'),errors="raise" )
        height = float(request.form.get('height'))
    except ValueError:
        flash('Please enter a date and a number')
    else:
        current_user.height.append(Height(date=date, height=height))
        db.session.commit()
    return redirect(url_for('main.height'))

@main.route('/plots/height')
@login_required
def plot_height():
    ds = get_data("height")
    p = setup_figure("Date", "Height [cm]")
    p.circle(
        x="Date", y="Height", size=10, color=colors[0], legend_label="Luan", source=ds
    )
    p.line(
        x="Date",
        y="Height",
        color=colors[0],
        line_width=3,
        line_dash="dashed",
        source=ds,
    )
    p.legend.location = "top_left"

    ref = get_reference_data("height")
    p.line(
        x="Date", y="P50", color="gray", line_width=2, legend_label="Median", source=ref
    )
    p.line(x="Date", y="P5", color="gray", line_width=1, line_dash="dotted", source=ref)
    p.line(
        x="Date", y="P10", color="gray", line_width=1, line_dash="dashed", source=ref
    )
    p.line(
        x="Date",
        y="P90",
        color="gray",
        line_width=1,
        line_dash="dashed",
        legend_label="90%",
        source=ref,
    )
    p.line(
        x="Date",
        y="P95",
        color="gray",
        line_width=1,
        line_dash="dotted",
        legend_label="95%",
        source=ref,
    )
    return json.dumps(json_item(p, "height"))
