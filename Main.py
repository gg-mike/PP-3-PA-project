from plot import *
from bokeh.plotting import output_file, show
from bokeh.models import Div

# example values
layout = column(
    Div(text="<h1>Cruise control (PI regulator)</h1>", align="center"),
    make_plot(start_velocity=0, end_velocity=50),
    make_plots(start_velocity=0, end_velocity=50)
)

output_file("cruise_control.html", title="Cruise control")

show(layout)
