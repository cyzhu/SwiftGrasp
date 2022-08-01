# import numpy as np
# import pandas as pd

# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import seaborn as sns

# from bokeh.io import show,  output_file
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    # LinearColorMapper,
    WheelZoomTool,
    LinearAxis,
    Range1d,
    # SingleIntervalTicker,
    NumeralTickFormatter,
    ResetTool,
    PanTool,
    # ColorBar,
    # Span,

)
from bokeh.plotting import figure
from bokeh.palettes import Category10


def line_plots(df, col_x, cols_y, cols_y2:list = None,title="Line charts",
            xRange:Range1d = None,yRange: Range1d = None, xlabel='Time',width=600, height=500):
    source = ColumnDataSource(data=df)
    p = figure(title=title, tools='hover',x_axis_type='datetime',width=width, height=height)

    color_length = len(cols_y)
    if cols_y2:
        color_length += len(cols_y2)
    # cl=inferno(color_length)
    # change the colorpalatte
    if color_length < 3:
        cl = Category10[3][:color_length]
    else:
        cl = Category10[color_length]
    i=0
    for name, color in zip( cols_y,  cl[:len(cols_y)]):
        pt=p.line(col_x,name, line_width=2, color = color, alpha=0.8,
                    muted_color=color, source=source, muted_alpha=0.2,legend_label=name)
        if i==0:
            hover = p.select(dict(type=HoverTool))
            hover.tooltips = [('Quarter',' @'+col_x+'{%F}'),(name,' @{'+name+'}{0,f}')]
            hover.formatters={'@'+col_x:'datetime'}
        else:
            p.add_tools(HoverTool(renderers=[pt],tooltips = [('Quarter',' @'+col_x+'{%F}'),(name,' @{'+name+'}{0,f}')],formatters={'@'+col_x:'datetime'}))
        i=i+1


    # xRange=Range1d(0, 100),yRange=Range1d(0,0.5)
    if xRange:
        p.x_range = xRange
    # p.xaxis.ticker = SingleIntervalTicker(interval=xtickinterval,desired_num_ticks = 1)
    if yRange:
        p.y_range = yRange
    # p.y_range.start = 0
    #p.legend.location = "center_right"
    #p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = xlabel
    # p.yaxis.axis_label = 'Percentage'
    p.grid.grid_line_color="gray"
    # p.yaxis.formatter = NumeralTickFormatter(format='0%')
    # hover = p.select(dict(type=HoverTool))
    # hover.tooltips = [('Percentage',' @Percentage{0.0%}'),('Count',' @Count{0,0}'),('Total','@Total{0,0}'),('Count range',' @left{0.00} to @right{0.00}')]
    
    if cols_y2:
        # Setting the second y axis range name and range
        y2_start = 0
        if all(max(df[col])<=1 for col in cols_y2):
            y2_end = 1
            mm = min(min(df[col]) for col in cols_y2)
            if mm < 0:
                from math import floor
                y2_start = floor(mm*10)/10.0
        else:
            y2_end = max(max(df[col]) for col in cols_y2)
        p.extra_y_ranges = {"Percentage": Range1d(start=y2_start, end=y2_end)}
        # Adding the second axis to the plot.  
        p.add_layout(LinearAxis(y_range_name="Percentage"), 'right')
        for name, color in zip( cols_y2, cl[len(cols_y):]):
            pt2=p.line(col_x,name, line_width=2, color = color, alpha=0.8,
                        muted_color=color, source=df[~df[name].isnull()], muted_alpha=0.2,legend_label=name,y_range_name="Percentage",line_dash="4 4")
            if y2_end == 1:
                fmt = '{0.0%}'
            else:
                fmt = '{0,f}'
            p.add_tools(HoverTool(renderers=[pt2],tooltips = [('Quarter',' @'+col_x+'{%F}'),(name,' @{'+name+'}'+fmt)],formatters={'@'+col_x:'datetime'}))
        if y2_end == 1:
            p.yaxis[1].formatter = NumeralTickFormatter(format='0%')
        # plot0 = p.line(x='left',y='cumsum',source=source,line_color="#e51d23",line_width=1.5, y_range_name="cumsum",line_dash="4 4")
        # p.add_tools(HoverTool(renderers=[plot0],tooltips = [('CumSum Percentage',' @cumsum{0.0%}'),('Factor range',' @left{0.00} to @right{0.00}')]))
    # p.ray(x=series.median(), y=0, length=1, angle=1.57079633, color='black',line_dash='4 4',line_width=1.5)
    # vline = Span(location=series.median(), dimension='height', line_color='#f9b612', line_dash='4 4',line_width=1.5)
    # # Horizontal line
    # hline = Span(location=0, dimension='width', line_color='green', line_width=3)

    # p.renderers.extend([vline])
    #p.legend.click_policy = "mute"
    p.toolbar.logo = None
    p.legend.location = "top_left"
    p.legend.click_policy="mute"
    p.add_tools(ResetTool(),WheelZoomTool(),PanTool())
    #output_file(title+".html")
    return p


