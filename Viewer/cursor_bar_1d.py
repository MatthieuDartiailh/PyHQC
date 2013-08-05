"""
"""
#TODO support hiding cursors, add default cursors preferences

# Use qt toolkit rather than wxWidget if another backend has not been set
# first
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import Str, HasTraits, Color, on_trait_change, Range,\
            Instance, Button, List, Int

from traitsui.api\
    import View, HGroup, Item, UItem, VGroup, Handler,\
            Spring, InstanceEditor, EnumEditor

from chaco.api\
    import DataView

import math

from float_display import FloatDisplay
from cursor_tool_1d import CursorTool1D
from has_preference_traits import HasPreferenceTraits

class EmptyCursorListView(HasTraits):
    """
    """

    name = Str('Click on the add cursor button to get a cursor')

    trait_view = View(UItem('name', style = 'readonly'))

class CursorListView(HasTraits):
    """
    """

    def __init__(self, list_cursors):

        super(CursorListView, self).__init__()
        aux = {}
        aux_view = []
        for i, cursor in enumerate(list_cursors):
            aux['cursor'+str(i)] = cursor
            aux_view.append(UItem('cursor'+str(i), style = 'custom',
                                  editor = InstanceEditor(view = 'bar_view'),
                                    ),
                            )

        self.trait_set(**aux)
        view = View(
                VGroup(aux_view),
                scrollable = True,
                height = -120,
                )

        self.trait_view('traits_view', view)

    def remove_class_trait(cls, name):
        """
        """
        cls._remove_class_trait(name)

    remove_class_trait = classmethod( remove_class_trait )

    def _remove_class_trait(cls, name):
        """
        """
        class_dict    = cls.__dict__
        class_traits = class_dict[ '__class_traits__' ]
        del class_traits[ name ]

    _remove_class_trait = classmethod( _remove_class_trait )

class CursorBar1DHandler(Handler):
    """
    """

    class_view = CursorListView

    def object_add_cursor_button_changed(self, info):
        """
        """

        cursor_bar = info.object
        index = len(cursor_bar.cursor_list)

        self.class_view.add_class_trait('cursor'+str(index),
                                        Instance(CursorTool1D))

        cursor_bar.add_cursor()
        cursor_bar.cursors_view = self.class_view(
                                    cursor_bar.cursor_list,
                                    )

    def object_remove_cursor_button_changed(self, info):
        """
        """

        cursor_bar = info.object
        index = len(cursor_bar.cursor_list)
        to_remove = []
        for i, cursor in enumerate(cursor_bar.cursor_list):
            if cursor.selected is True:
                self.class_view.remove_class_trait('cursor'+str(index-1-i))
                to_remove.append(cursor)

        cursor_bar.remove_cursors(to_remove)
        if cursor_bar.cursor_list:
            cursor_bar.cursors_view = self.class_view(
                                        cursor_bar.cursor_list,
                                        )
        else:
            cursor_bar.cursors_view = EmptyCursorListView()

class CursorBar1D(HasPreferenceTraits):
    """
    """

    plot = Instance(DataView)
    cursor_list = List(Instance(CursorTool1D))
    cursor_list_name = List(Str, [])
    available_names = List(Str, [])
    auto_color_list = List(["red" , "blue", "green", "lightblue",
                        "pink", "silver"])
    available_colors = List(Color, [])
    default_format = Str('g', preference = 'async')
    default_digits = digits = Range(low = 0, high = 8, value = 4,
                                    mode = 'spinner', preference = 'async')

    add_cursor_button = Button(style = 'toolbar', label = 'Add')
    remove_cursor_button = Button(style = 'toolbar', label = 'Remove')

    cursor1_name = Str()
    cursor1_ind = Int
    cursor2_name = Str()
    cursor2_ind = Int
    delta_x = Instance(FloatDisplay)
    delta_y = Instance(FloatDisplay)
    delta  = Instance(FloatDisplay)
    delta_prop = Button(type = 'toolbar', label = 'P',
                        width_padding = 0, orientation = 'horizontal')

    cursors_view = Instance(HasTraits)

    traits_view = View(
                    HGroup(
                        VGroup(
                            HGroup(
                                UItem('add_cursor_button'),
                                UItem('remove_cursor_button'),
                                ),
                            UItem('cursors_view', style = 'custom',
                                  height = -110),
                            ),
                        VGroup(
                            HGroup(
                                Spring(),
                                Item('cursor1_name',
                                        label = 'C 1',
                                        width = 100,
                                        editor = EnumEditor(
                                                name = 'cursor_list_name'),
                                    ),
                                Spring(),
                                Item('cursor2_name',
                                        label = 'C 2',
                                        width = 100,
                                        editor = EnumEditor(
                                                name = 'cursor_list_name'),
                                    ),
                                Spring()
                                ),
                            HGroup(
                                Spring(),
                                Item('object.delta_x.display',
                                        label = 'dX', style = 'readonly'),
                                Spring(),
                                Item('object.delta_y.display',
                                        label = 'dY', style = 'readonly'),
                                Spring()
                                ),
                            HGroup(
                                Spring(),
                                Item('object.delta.display',
                                        label = 'd', style = 'readonly'),
                                Spring(),
                                UItem('delta_prop',
                                      style = 'custom', width = -20),
                                Spring()),
                            label = 'Distances',
                            show_border = True,
                            ),
                        ),
                    handler = CursorBar1DHandler(),
                    )


    def __init__(self, plot, **kwargs):
        """
        """
        super(CursorBar1D, self).__init__(**kwargs)
        self.plot = plot
        self.delta_x = FloatDisplay(0.0, pref_name = 'Delta x',
                                    pref_parent = self)
        self.delta_y = FloatDisplay(0.0, pref_name = 'Delta y',
                                    pref_parent = self)
        self.delta  = FloatDisplay(0.0, pref_name = 'Delta',
                                    pref_parent = self)
        self.cursors_view = EmptyCursorListView()

        self.preference_init()

    @on_trait_change('cursor_list:name')
    def update_list_name(self, obj, name, old, new):
        """
        """
        i = None
        for ind, cursor in enumerate(self.cursor_list):
            if cursor.name == new:
                i = ind
                break

        self.cursor_list_name[i] = new
        if old == self.cursor1_name:
            self.cursor1_name = new
        if old == self.cursor2_name:
            self.cursor2_name = new


    def add_cursor(self):
        """
        """

        name = ''
        if not self.available_names:
            name = 'Cursor {}'.format(len(self.cursor_list)+1)
        else:
            name = self.available_names.pop(-1)

        if not self.available_colors:
            color = self.auto_color_list[len(self.cursor_list)]
        else:
            color = self.available_colors.pop(-1)

        cursor = CursorTool1D(self.plot, name = name, color = color)
        self.cursor_list.append(cursor)
        self.cursor_list_name.append(name)

    def remove_cursors(self, item_list):
        """
        """
        for item in item_list:
            self.plot.overlays.remove(item.cursor)
            self.available_names.append(item.name)
            self.available_colors.append(item.color)
            if self.cursor_list[self.cursor1_ind] == item:
                self.cursor1_name = ''
                self.cursor1_ind = -1
                self.disconnect_delta_to_cursors()
            elif self.cursor_list[self.cursor2_ind] == item:
                self.cursor2_name = ''
                self.cursor2_ind = -1
                self.disconnect_delta_to_cursors()
            self.cursor_list_name.remove(item.name)
            self.cursor_list.remove(item)
        self.plot.request_redraw()

    @on_trait_change('cursor1_name, cursor2_name')
    def update_cursor(self, name, new):
        """
        """
        for ind, cursor in enumerate(self.cursor_list):
            if cursor.name == new:
                if 'cursor1' in name:
                    self.cursor1_ind = ind
                else:
                    self.cursor2_ind = ind
                break

        if self.cursor1_ind > -1 and self.cursor2_ind > -1:
            self.connect_delta_to_cursors()

    def update_delta(self):
        """
        """
        c_1 = self.cursor_list[self.cursor1_ind]
        c_2 = self.cursor_list[self.cursor2_ind]
        x_1 = c_1.index.value
        x_2 = c_2.index.value
        y_1 = c_1.value.value
        y_2 = c_2.value.value
        self.delta_x.value = x_1-x_2
        self.delta_y.value = y_1-y_2
        self.delta.value  = math.sqrt((x_1-x_2)**2+(y_1-y_2)**2)

    def connect_delta_to_cursors(self):
        """
        """
        string = 'index:value,value:value'
        c_1 = self.cursor1_ind
        c_2 = self.cursor2_ind
        self.cursor_list[c_1].on_trait_change(self.update_delta, name = string)
        self.cursor_list[c_2].on_trait_change(self.update_delta, name = string)
        self.update_delta()

    def disconnect_delta_to_cursors(self):
        string = 'index:value,value:value'
        c_1 = self.cursor1_ind
        c_2 = self.cursor2_ind
        self.cursor_list[c_1].on_trait_change(self.update_delta, name = string,
                                              remove = True)
        self.cursor_list[c_2].on_trait_change(self.update_delta, name = string,
                                              remove = True)

if __name__ == '__main__':
    from numpy import linspace, sin
    from enable.component_editor import ComponentEditor
    from chaco.api import  ArrayPlotData,\
                            add_default_axes
    from plot_1d import Plot1D

    class ScatterPlotTraits(HasTraits):

        plot = Instance(DataView)
        view = Instance(View)
        cursor_bar = Instance(CursorBar1D)

        def __init__(self):
            super(ScatterPlotTraits, self).__init__()

            x = linspace(-14, 14, 100)
            y = sin(x) * x**3
            y2 = 2*y
            plotdata = ArrayPlotData(x = x)
            plotdata.set_data('y',y)
            plotdata.set_data('y2', y2)

            self.plot = Plot1D(plotdata)
            self.plot.x_grid.line_color = 'yellow'
            self.plot.y_grid.line_color = 'yellow'
            # Can be used for
            line = self.plot.plot(("x", "y"), name = 'line', type="line",
                                  color="white")[0]
            self.cursor_bar = CursorBar1D(self.plot)
            add_default_axes(line,vtitle = 'toto', htitle = 'hh')

        view = View(
                VGroup(Item('plot', editor=ComponentEditor(), show_label=False),
                   UItem('cursor_bar', style = 'custom',
                         height = -120)),
                width=-1, height=600,
                resizable=True, title="Chaco Plot")

    ScatterPlotTraits().configure_traits()