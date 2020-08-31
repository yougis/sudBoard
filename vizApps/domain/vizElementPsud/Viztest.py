import numpy as np
import param
import holoviews as hv

import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from vizApps.domain.TypeVizEnum import  TypeVizEnum


class BaseClass(param.Parameterized):
    x                       = param.Parameter(default=3.14, doc="X position")
    y                       = param.Parameter(default="Not editable", constant=True)
    string_value            = param.String(default="str", doc="A string")
    num_int                 = param.Integer(50000, bounds=(-200, 100000))
    unbounded_int           = param.Integer(23)
    float_with_hard_bounds  = param.Number(8.2, bounds=(7.5, 10))
    float_with_soft_bounds  = param.Number(0.5, bounds=(0, None), softbounds=(0,2))
    unbounded_float         = param.Number(30.01, precedence=0)
    hidden_parameter        = param.Number(2.718, precedence=-1)
    integer_range           = param.Range(default=(3, 7), bounds=(0, 10))
    float_range             = param.Range(default=(0, 1.57), bounds=(0, 3.145))
    dictionary              = param.Dict(default={"a": 2, "b": 9})


class VizParamsExemple(param.Parameterized):


    offset = param.Number(default=0.0, bounds=(-5.0, 5.0))
    amplitude = param.Number(default=1.0, bounds=(-5.0, 5.0))
    phase = param.Number(default=0.0, bounds=(0.0, 2 * np.pi))
    frequency = param.Number(default=1.0, bounds=(0.1, 5.1))
    N = param.Integer(default=200, bounds=(0, None))
    x_range = param.Range(default=(0, 4 * np.pi), bounds=(0, 4 * np.pi))
    y_range = param.Range(default=(-2.5, 2.5), bounds=(-10, 10))

    def __init__(self, **params):
        super(VizParamsExemple, self).__init__(**params)
        self.type = TypeVizEnum.LINE_GRAPH
        x, y = self.sine()
        self.cds = ColumnDataSource(data=dict(x=x, y=y))
        self.plot = figure(plot_height=400, plot_width=400,
                           tools="crosshair, pan, reset, save, wheel_zoom",
                           x_range=self.x_range, y_range=self.y_range)
        self.plot.line('x', 'y', source=self.cds, line_width=3, line_alpha=0.6)

    @param.depends('N', 'frequency', 'amplitude', 'offset', 'phase', 'x_range', 'y_range', watch=True)
    def update_plot(self):
        x, y = self.sine()
        self.cds.data = dict(x=x, y=y)
        self.plot.x_range.start, self.plot.x_range.end = self.x_range
        self.plot.y_range.start, self.plot.y_range.end = self.y_range

    def sine(self):
        x = np.linspace(0, 4 * np.pi, self.N)
        y = self.amplitude * np.sin(self.frequency * x + self.phase) + self.offset
        return x, y

    @param.depends('N','phase')
    def view(self):
        line = (self.N,self.phase)
        return hv.Line(line)