from bokeh.models import DateFormatter, ColumnDataSource, RadioButtonGroup
from bokeh.models.widgets import DataTable, TableColumn, Button, TextInput
from bokeh.models.widgets import DatePicker
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.layouts import row, column
from bokeh.plotting import figure

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from flask_login import login_required, current_user

n_rolling = 5
colors = "#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"

days = 1000 * 60 * 60 * 24  # milliseconds


def get_data(name, index=False):
    if name in ["weight", "height"]:
        try:
            date, values = zip(*[(x.date, x.value) for x in current_user.children[0].measurements.filter_by(m_type=name)])
            print(values)
        except ValueError:
            date, values = [], []
        return ColumnDataSource({"Date": date, name.capitalize(): values})
    df = pd.read_csv(f"{name}.csv")
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    ds = ColumnDataSource(df.set_index("Date"), name=name)
    return ds


def get_reference_data(name):
    ref = pd.read_csv(f"reference_{name}.csv")
    start = current_user.children[0].birth_date
    diff = (datetime.now() - start).days // 7 + 1
    ref["Date"] = start + pd.to_timedelta(ref["Week"], unit="W")
    ref = ref.set_index("Date").iloc[: diff + 1]
    if name == "weight":
        ref = ref.multiply(1000)
    ref_ds = ColumnDataSource(ref)
    return ref_ds


def setup_figure(xlabel, ylabel):
    p = figure(
        # width=800,
        # height=600,
        x_axis_label=xlabel,
        y_axis_label=ylabel,
        x_axis_type="datetime",
        tools="save,pan,wheel_zoom,box_zoom,reset",
        toolbar_location="above",
        active_drag=None,
        active_scroll=None,
        sizing_mode="stretch_width",
        #aspect_ratio=16/9,
        min_border_left=0,
    )
    p.toolbar.autohide = True
    p.xaxis.formatter = DatetimeTickFormatter(days=["%d.%m"])
    p.xaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_text_font_style = "normal"
    p.xaxis.axis_label_text_font_size = "3vmin"
    p.xaxis.major_label_text_font_size = "3vmin"
    p.yaxis.axis_label_text_font_size = "3vmin"
    p.yaxis.major_label_text_font_size = "3vmin"
    p.outline_line_color = None
    p.grid.grid_line_color = None
    return p
