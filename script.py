from random import random
import threading
import numpy as np
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, LinearAxis, Range1d, Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc, show

import UpdateListener


# create a callback that adds a number in a random location
class figureTemp(object):

    def __init__(self) -> None:

        self.db_file = "./data/mainds.db"
        self.db_name = "AirData"
        self.list_of_variables = ['datetime', 'temp', 'pressure', 'humidity', 'eco2']
        self.var_2_idx = {elem: idx for idx,elem in enumerate(self.list_of_variables)}

        self.db = UpdateListener.database(
            filepath = self.db_file, 
            dataset  = self.db_name,
            t_listen = 3, 
            callback_func = self.setNewDataFl
        )

        data = self.db.getCursor(','.join(self.list_of_variables)).fetchall()
        self.__fl_new_data = False

        dates = np.array([x[self.var_2_idx['datetime']] for x in data], dtype=np.datetime64)
        self.src = ColumnDataSource(
            data=dict(dtm=dates, 
                      temp=[x[self.var_2_idx['temp']] for x in data], 
                      hum=[x[self.var_2_idx['humidity']] for x in data])
        )

        self.p = figure(width=700, height=700,x_axis_type="datetime")
        self.p.line('dtm', 'temp', legend_label="Temperature", source=self.src, line_color="darkcyan", line_width=3)

        self.p.extra_y_ranges['hum'] = Range1d(0, 100)
        self.p.yaxis.axis_label = "Temperature, °C"
        self.p.xaxis.axis_label = "Datetime"
        
        
        ax2 = LinearAxis(
            axis_label="Humidity, %",
            y_range_name="hum",
        )

        self.p.add_layout(ax2, 'right')
        self.p.line('dtm', 'hum', legend_label="Humidity", source=self.src, line_color="darkorange", y_range_name="hum", line_width=3)


        curdoc().add_periodic_callback(self.__updatedata, 10)
        curdoc().add_root(self.p)

    def setNewDataFl(self) -> None:
        self.__fl_new_data = True


    def __updatedata(self) -> None:
        if self.__fl_new_data == False:
            return
        new_data = self.db.getCursor(','.join(self.list_of_variables)).fetchall()
        if new_data != None and len(new_data) > 0:
            dates = np.array([x[self.var_2_idx['datetime']] for x in new_data], dtype=np.datetime64)
            temp = [x[self.var_2_idx['temp']] for x in new_data]
            hum = [x[self.var_2_idx['humidity']] for x in new_data]

            print(dict(dtm=dates, temp=temp, hum=hum))
            self.src.stream(dict(dtm=dates, temp=temp, hum=hum))

fig = figureTemp()




