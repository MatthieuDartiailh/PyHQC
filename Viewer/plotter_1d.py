"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import Str, Instance

from traitsui.api\
    import View, UItem, Group, HGroup, VGroup, InstanceEditor, Item

from enable.component_editor\
    import ComponentEditor

from chaco.api\
    import ArrayPlotData

import numpy

from has_preference_traits import HasPreferenceTraits
from plot_1d import Plot1D
from zoom_bar import ZoomBar, zoom_bar
from pan_bar import PanBar
from range_bar import RangeBar
from cursor_bar_1d import CursorBar1D
from axis_formatter import AxisFormatter

class Plotter1D(HasPreferenceTraits):
    """
    """
    #Main components
    plot = Instance(Plot1D)
    data = Instance(ArrayPlotData,())

    #Plot tools
    zoom_bar = Instance(ZoomBar)
    pan_bar = Instance(PanBar)
    range_bar = Instance(RangeBar)
    cursor_bar = Instance(CursorBar1D) #This one holds preferences

    #Axis properties
    x_axis_label = Str
    y_axis_label = Str
    x_axis_formatter = Instance(AxisFormatter) #This one holds preferences
    y_axis_formatter = Instance(AxisFormatter) #This one holds preferences

    traits_view = View(
                    Group(
                        UItem('plot', editor = ComponentEditor()),
                        Group(
                            Group(
                                VGroup(
                                    HGroup(
                                        UItem('zoom_bar', style = 'custom'),
                                        UItem('pan_bar', style = 'custom'),
                                        ),
                                    UItem('range_bar', style = 'custom'),
                                ),
                                UItem('cursor_bar', style = 'custom',
                                      height = -120),
                                orientation = 'horizontal',
                                ),
                            orientation = 'vertical',
                            ),
                        orientation = 'vertical',
                        ),
                    resizable = True
                    )

    preference_view = View(
                        HGroup(
                            VGroup(
                                Item('x_axis_formatter', style = 'custom',
                                     editor = InstanceEditor(
                                                 view = 'preference_view'),
                                     label = 'X axis',
                                     ),
                                Item('y_axis_formatter', style = 'custom',
                                     editor = InstanceEditor(
                                                 view = 'preference_view'),
                                     label = 'Y axis',
                                     ),
                                show_border = True,
                                label = 'Axis format',
                                ),
                            VGroup(
                                UItem('cursor_bar', style = 'custom',
                                      editor = InstanceEditor(
                                                 view = 'preference_view'),
                                    ),
                                show_border = True,
                                label = 'Default cursor format',
                                ),
                            ),
                        )

    def __init__(self, **kwarg):

        super(Plotter1D, self).__init__(**kwarg)

        #axis formatter init
        self.x_axis_formatter = AxisFormatter(pref_name = 'X axis format',
                                              pref_parent = self)
        self.y_axis_formatter = AxisFormatter(pref_name = 'Y axis format',
                                              pref_parent = self)

        #Plot init
        self.data = ArrayPlotData()
        self.plot = Plot1D(self.data)
        self.plot.padding = (80,40,10,40)
        self.plot.x_axis.tick_label_formatter =\
                        self.x_axis_formatter.float_format
        self.plot.y_axis.tick_label_formatter =\
                        self.y_axis_formatter.float_format

        #Tools init and connection
        self.cursor_bar = CursorBar1D(self.plot, pref_name = 'Cursor bar',
                                      pref_parent = self)
        self.pan_bar = PanBar(self.plot)
        self.zoom_bar = zoom_bar(self.plot,x = True, y = True, reset = True)
        self.range_bar = RangeBar(self.plot)
        self.x_axis_label = 'X'
        self.y_axis_label = 'Y'
        self.on_trait_change(self.new_x_label, 'x_axis_label',
                             dispatch = 'ui')
        self.on_trait_change(self.new_y_label, 'y_axis_label',
                             dispatch = 'ui')
        self.on_trait_change(self.new_x_axis_format, 'x_axis_formatter.+',
                             dispatch = 'ui')
        self.on_trait_change(self.new_y_axis_format, 'y_axis_formatter.+',
                             dispatch = 'ui')

        self.preference_init()

    #@on_trait_change('x_axis_label', dispatch = 'ui')
    def new_x_label(self,new):
        """
        """
        self.plot.x_axis.title = new
        self.range_bar.x_name = new

    #@on_trait_change('y_axis_label', dispatch = 'ui')
    def new_y_label(self,new):
        """
        """
        self.plot.y_axis.title = new
        self.range_bar.y_name = new

    #@on_trait_change('x_axis_formatter.+', dispatch = 'ui')
    def new_x_axis_format(self):
        """
        """
        self.plot.x_axis._invalidate()
        self.plot.invalidate_and_redraw()

    #@on_trait_change('y_axis_formatter.+', dispatch = 'ui')
    def new_y_axis_format(self):
        """
        """
        self.plot.y_axis._invalidate()
        self.plot.invalidate_and_redraw()

class AutoPlotter1D(Plotter1D):
    """
    """

    def __init__(self, **kwargs):
        super(AutoPlotter1D, self).__init__(**kwargs)
        self.on_trait_change(self.auto_plot_data, 'data:data_changed',
                             dispatch = 'ui')

    #@on_trait_change('data:data_changed', dispacth = 'ui')
    def auto_plot_data(self,new):
        """
        """
        if new.has_key("removed"):
            aux = []
            for deleted in new['removed']:
                if deleted is not 'x':
                    aux.append(deleted)
            self.plot.delplot(*tuple(aux))

        if new.has_key("added"):
            for added in new['added']:
                if added is not 'x':
                    self.plot.plot(('x', added),\
                            name = added, type = 'line', color = 'auto')

        if new.has_key("changed"):
            pass

if __name__ == "__main__":

    plotter = AutoPlotter1D()
    x = numpy.linspace(0, 1, 100)
    y0 = numpy.sin(x)
    plotter.data.set_data('x',x)
    plotter.data.set_data('y0',y0)
    plotter.x_axis_formatter = AxisFormatter('e')
    plotter.y_axis_formatter = AxisFormatter('e')
    plotter.configure_traits()