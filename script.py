import threading
import json
import numpy as np

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, LinearAxis, Range1d, Button, DatePicker, SVGIcon
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc, show
from datetime import datetime
from DbUpdater import updateDB

from svg_library import svg_icon1, svg_icon2, svg_icon3, svg_water1, svg_water2, svg_water3

import UpdateListener

class figureTemp(object):

    def __init__(self) -> None:

        self.figure_mode = 1

        self.db_file = "./data/AirData.db"
        self.db_name = "AirData"

        self.start_date = "2023-11-19"
        self.end_date = "2023-11-19"

        self.list_of_variables1 = ['datetime', 'temp', 'pressure', 'humidity', 'eco2']
        self.var_2_idx1 = {elem: idx for idx,elem in enumerate(self.list_of_variables1)}

        self.list_of_variables2 = ['datetime', 'moist1', 'moist2', 'moist3']
        self.var_2_idx2 = {'datetime':0, 'temp':1, 'pressure':1, 'humidity':2, 'eco2':3}

        self.list_of_variables = self.list_of_variables1
        self.var_2_idx = self.var_2_idx1

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
                      hum=[x[self.var_2_idx['humidity']] for x in data],
                      eco2=[x[self.var_2_idx['eco2']] for x in data])
        )

        self.p = figure(width=700, height=700,x_axis_type="datetime", y_range=Range1d(0, 30))

        self.line1 = self.p.line('dtm', 'temp', legend_label="Temperature", source=self.src, line_color="darkcyan", line_width=3)
        self.scatter1 = self.p.scatter('dtm','temp', source=self.src, marker='asterisk', line_color='#267574', size=5)

        self.p.extra_y_ranges['hum'] = Range1d(0, 100)
        self.p.yaxis.axis_label = "Temperature, °C"
        self.p.xaxis.axis_label = "Datetime"

        ax2 = LinearAxis(
            axis_label="Humidity, %",
            y_range_name="hum",
        )

        self.p.add_layout(ax2, 'right')

        self.line2 = self.p.line('dtm', 'hum', legend_label="Humidity", source=self.src, line_color="darkorange", y_range_name="hum", line_width=3)
        self.scatter2 = self.p.scatter('dtm', 'hum', source=self.src, marker='asterisk', line_color="#D17814", size=5, y_range_name="hum")

        self.line3 = self.p.line('dtm', 'hum', source=self.src, line_color="darkorange", line_width=3)
        self.scatter3 = self.p.scatter('dtm', 'hum', source=self.src, marker='asterisk', line_color="#D17814", size=5)
        self.scatter3.update(visible=False)
        self.line3.update(visible=False)


        self.line4 = self.p.line('dtm', 'eco2', source=self.src, line_color="olive", line_width=3)
        self.scatter4 = self.p.scatter('dtm', 'eco2', source=self.src, marker='asterisk', line_color="#626302", size=5)
        self.scatter4.update(visible=False)
        self.line4.update(visible=False)


        curdoc().add_periodic_callback(self.__updatedata, 10)


        def change_start_date(attrname, old, new):
            self.start_date = new
            self.p.x_range.update(start = int(datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()*1000),
                                  end = int(datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()*1000))

        def change_end_date(attrname, old, new):
            self.end_date = new
            self.p.x_range.update(start = int(datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()*1000),
                                  end = int(datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()*1000))

        self.stdt_picker = DatePicker(title='Select start date', value=self.start_date, min_date="2023-11-19")
        self.endt_picker = DatePicker(title='Select end date', value=self.end_date, min_date="2023-11-19")

        self.stdt_picker.on_change('value', change_start_date)
        self.endt_picker.on_change('value', change_end_date)

        icon_water = SVGIcon(name="water", svg=svg_icon1, size = '7em')

        icon_planet = SVGIcon(name="planet", svg=svg_icon2, size = '7em')

        icon_house = SVGIcon(name="house", svg=svg_icon3, size = '7em')

        icon_water1 = SVGIcon(name="water1", svg=svg_water1, size = '7em')
        icon_water2 = SVGIcon(name="water1", svg=svg_water2, size = '7em')
        icon_water3 = SVGIcon(name="water1", svg=svg_water3, size = '7em')

        def __on_click_button(button_num, buttons):

            def __callback():
                self.mode = button_num
                for i in buttons:
                    i.update(button_type="default")
                buttons[button_num].update(button_type="primary")
                if button_num == 0:
                    self.line2.update(visible=True)
                    self.scatter2.update(visible=True)
                    self.line3.update(visible=False)
                    self.scatter3.update(visible=False)
                    self.line4.update(visible=False)
                    self.scatter4.update(visible=False)
                    self.p.legend.update(visible=True)

                    for i in ("dtm", "temp", "hum", "eco2"):
                        self.src.remove(i)
                    for i in ("dtm", "temp", "hum", "eco2"):
                        if i == "dtm":
                            self.src.add(data=np.array([], dtype=np.datetime64), name=i)
                        else:
                            self.src.add(data=np.array([]), name=i)

                    self.db.attachNewDb(filepath='./data/AirData.db', dataset="AirData")
                    self.var_2_idx = self.var_2_idx1
                    self.list_of_variables = self.list_of_variables1
                    self.setNewDataFl()
                    self.__updatedata()

                    self.p.y_range.start = 0
                    self.p.y_range.end = 30
                    self.p.x_range.start = int(datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()*1000)
                    self.p.x_range.end = int(datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()*1000)

                if button_num != 0:
                    self.line2.update(visible=False)
                    self.scatter2.update(visible=False)
                    self.line3.update(visible=True)
                    self.scatter3.update(visible=True)
                    self.line4.update(visible=True)
                    self.scatter4.update(visible=True)

                    self.p.legend.update(visible=False)

                    for i in ("dtm", "temp", "hum", "eco2"):
                        self.src.remove(i)
                    for i in ("dtm", "temp", "hum", "eco2"):
                        if i == "dtm":
                            self.src.add(data=np.array([], dtype=np.datetime64), name=i)
                        else:
                            self.src.add(data=np.array([]), name=i)

                    self.db.attachNewDb(filepath='./data/Plants.db', dataset="moist")
                    self.var_2_idx = self.var_2_idx2
                    self.list_of_variables = self.list_of_variables2
                    self.setNewDataFl()
                    self.__updatedata()

                    self.p.y_range.start = 0
                    self.p.y_range.end = 1000
                    self.p.x_range.start = int(datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()*1000)
                    self.p.x_range.end = int(datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()*1000)

                if button_num == 2:
                    self.buttonwater1.update(visible=True)
                    self.buttonwater2.update(visible=True)
                    self.buttonwater3.update(visible=True)
                else:
                    self.buttonwater1.update(visible=False)
                    self.buttonwater2.update(visible=False)
                    self.buttonwater3.update(visible=False)



            return __callback

        self.button1 = Button(label="", button_type="primary", width=128, height = 128, icon=icon_planet)
        self.button2 = Button(label="", button_type="default", width=128, height = 128, icon=icon_house)
        self.button3 = Button(label="", button_type="default", width=128, height = 128, icon=icon_water)

        def __on_click_water_flowers(num_flower):

            def __callback():
                updateDB(json.loads('{{"dbname":"Plants.db","dsname":"waterplant","plantnum":"{}"}}'.format(num_flower)))

            return __callback;

        self.buttonwater1 = Button(label="", button_type="default", width=128, height = 128, icon=icon_water1, visible=False)
        self.buttonwater2 = Button(label="", button_type="default", width=128, height = 128, icon=icon_water2, visible=False)
        self.buttonwater3 = Button(label="", button_type="default", width=128, height = 128, icon=icon_water3, visible=False)

        self.button1.on_click(__on_click_button(0, [self.button1, self.button2, self.button3]))
        self.button2.on_click(__on_click_button(1, [self.button1, self.button2, self.button3]))
        self.button3.on_click(__on_click_button(2, [self.button1, self.button2, self.button3]))

        self.buttonwater1.on_click(__on_click_water_flowers(1))
        self.buttonwater2.on_click(__on_click_water_flowers(2))
        self.buttonwater3.on_click(__on_click_water_flowers(3))


        buttons = row(self.button1, self.button2, self.button3, self.buttonwater1, self.buttonwater2, self.buttonwater3)
        inputPanel = column(buttons, row(self.stdt_picker, self.endt_picker))
        document = column(inputPanel, self.p, name='mainLayout')

        curdoc().add_root(document)



    def setNewDataFl(self) -> None:
        self.__fl_new_data = True


    def __updatedata(self) -> None:
        if self.__fl_new_data == False:
            return
        print("Updating data")
        new_data = self.db.getCursor(','.join(self.list_of_variables)).fetchall()
        self.__fl_new_data = False
        if new_data != None and len(new_data) > 0:
            dates = np.array([x[self.var_2_idx['datetime']] for x in new_data], dtype=np.datetime64)
            temp = [x[self.var_2_idx['temp']] for x in new_data]
            hum = [x[self.var_2_idx['humidity']] for x in new_data]
            eco2 = [x[self.var_2_idx['eco2']] for x in new_data]

#            print(dict(dtm=dates, temp=temp, hum=hum))
            self.src.stream(dict(dtm=dates, temp=temp, hum=hum, eco2=eco2))

fig = figureTemp()




