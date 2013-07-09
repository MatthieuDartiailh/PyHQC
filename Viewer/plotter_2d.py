from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import  Str, Instance, Bool, on_trait_change, Float, Enum, Trait, Callable

from traitsui.api\
    import View, UItem, VGroup, Group, Item, InstanceEditor, HGroup

from enable.component_editor\
    import ComponentEditor

from chaco.api\
    import ArrayPlotData, ColorBar, LinearMapper, HPlotContainer,\
        GridDataSource, ImagePlot, CMapImagePlot, ContourPolyPlot

from chaco.tools.api\
    import PanTool

from chaco.default_colormaps import color_map_name_dict, Greys

from numpy import cosh, exp, linspace, meshgrid, tanh

from has_preference_traits import HasPreferenceTraits
from plot_2d import Plot2D
from zoom_bar import zoom_bar, ZoomBar
from pan_bar import PanBar
from range_bar import RangeBar
from axis_formatter import AxisFormatter

class Plotter2D(HasPreferenceTraits):

    plot = Instance(Plot2D)
    colorbar = Instance(ColorBar)
    container = Instance(HPlotContainer)

    zoom_bar_plot = Instance(ZoomBar)
    zoom_bar_colorbar = Instance(ZoomBar)
    pan_bar = Instance(PanBar)
    range_bar = Instance(RangeBar)

    data = Instance(ArrayPlotData,())
    x_min = Float(0.0)
    x_max = Float(1.0)
    y_min = Float(0.0)
    y_max = Float(1.0)

    add_contour = Bool(False)
    x_axis_label = Str
    y_axis_label = Str
    c_axis_label = Str

    x_axis_formatter = Instance(AxisFormatter)
    y_axis_formatter = Instance(AxisFormatter)
    c_axis_formatter = Instance(AxisFormatter)

    colormap = Enum(color_map_name_dict.keys(), preference = 'async')
    _cmap = Trait(Greys, Callable)

    traits_view = View(
                    Group(
                        Group(
                            UItem('container', editor=ComponentEditor()),
                            VGroup(
                                UItem('zoom_bar_colorbar',style = 'custom'),
                                ),
                            orientation = 'horizontal',
                            ),
                        Group(
                            Group(
                                UItem('zoom_bar_plot', style = 'custom'),
                                UItem('pan_bar', style = 'custom'),
                                UItem('range_bar', style = 'custom'),
                                Group(
                                    UItem('colormap'),
                                    label = 'Color map',
                                    ),
                                orientation = 'horizontal',
                                ),
                            orientation = 'vertical',
                            ),
                        orientation = 'vertical',
                        ),
                    resizable=True
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
                                ),
                            Item('c_axis_formatter', style = 'custom',
                                 editor = InstanceEditor(
                                             view = 'preference_view'),
                                 label = 'C axis',
                                 ),
                            show_border = True,
                            label = 'Axis format',
                            ),
                        )

    def __init__(self, **kwargs):

        super(Plotter2D, self).__init__(**kwargs)

        self.x_axis_formatter = AxisFormatter(pref_name = 'X axis format',
                                              pref_parent = self)
        self.y_axis_formatter = AxisFormatter(pref_name = 'Y axis format',
                                              pref_parent = self)
        self.c_axis_formatter = AxisFormatter(pref_name = 'C axis format',
                                              pref_parent = self)

        self.data = ArrayPlotData()
        self.plot = Plot2D(self.data)
        self.plot.padding = (80,50,10,40)
        self.plot.x_axis.tick_label_formatter =\
                        self.x_axis_formatter.float_format
        self.plot.y_axis.tick_label_formatter =\
                        self.y_axis_formatter.float_format
        self.pan_bar = PanBar(self.plot)
        self.zoom_bar_plot = zoom_bar(self.plot,x = True,\
                                        y = True, reset = True
                                        )

        #Dummy plot so that the color bar can be correctly initialized
        xs = linspace(-2, 2, 600)
        ys = linspace(-1.2, 1.2, 300)
        self.x_min = xs[0]
        self.x_max = xs[-1]
        self.y_min = ys[0]
        self.y_max = ys[-1]
        x, y = meshgrid(xs,ys)
        z = tanh(x*y/6)*cosh(exp(-y**2)*x/3)
        z = x*y
        self.data.set_data('c',z)
        self.plot.img_plot(('c'),\
                                name = 'c',
                                colormap = self._cmap,
                                xbounds = (self.x_min,self.x_max),
                                ybounds = (self.y_min,self.y_max),
                                )

        # Create the colorbar, the appropriate range and colormap are handled
        # at the plot creation

        self.colorbar = ColorBar(
                            index_mapper = LinearMapper(range = \
                                            self.plot.color_mapper.range),
                            color_mapper=self.plot.color_mapper,
                            plot = self.plot,
                            orientation='v',
                            resizable='v',
                            width=20,
                            padding=10)

        self.colorbar.padding_top = self.plot.padding_top
        self.colorbar.padding_bottom = self.plot.padding_bottom

        self.colorbar._axis.tick_label_formatter =\
                                self.c_axis_formatter.float_format

        self.container = HPlotContainer(self.plot,
                                    self.colorbar,
                                    use_backbuffer=True,
                                    bgcolor="lightgray")

        # Add pan and zoom tools to the colorbar
        self.colorbar.tools.append(PanTool(self.colorbar,\
                                        constrain_direction="y",\
                                        constrain=True)
                                )
        self.zoom_bar_colorbar = zoom_bar(self.colorbar,
                                          box = False,
                                          reset=True,
                                          orientation = 'vertical'
                                        )

        # Add the range bar now that we are sure that we have a color_mapper
        self.range_bar = RangeBar(self.plot)
        self.x_axis_label = 'X'
        self.y_axis_label = 'Y'
        self.c_axis_label = 'C'
        self.sync_trait('x_axis_label',self.range_bar,alias = 'x_name')
        self.sync_trait('y_axis_label',self.range_bar,alias = 'y_name')
        self.sync_trait('c_axis_label',self.range_bar,alias = 'c_name')

        #Dynamically bing the update methods for trait likely to be updated
        #from other thread
        self.on_trait_change(self.new_x_label, 'x_axis_label',
                             dispatch = 'ui')
        self.on_trait_change(self.new_y_label, 'y_axis_label',
                             dispatch = 'ui')
        self.on_trait_change(self.new_c_label, 'c_axis_label',
                             dispatch = 'ui')
        self.on_trait_change(self.new_x_axis_format, 'x_axis_formatter.+',
                             dispatch = 'ui')
        self.on_trait_change(self.new_y_axis_format, 'y_axis_formatter.+',
                             dispatch = 'ui')
        self.on_trait_change(self.new_c_axis_format, 'c_axis_formatter.+',
                             dispatch = 'ui')

        #set the default colormap in the editor
        self.colormap = 'Blues'

        self.preference_init()

    #@on_trait_change('x_axis_label', dispatch = 'ui')
    def new_x_label(self,new):
        self.plot.x_axis.title = new

    #@on_trait_change('y_axis_label', dispatch = 'ui')
    def new_y_label(self,new):
        self.plot.y_axis.title = new

    #@on_trait_change('c_axis_label', dispatch = 'ui')
    def new_c_label(self,new):
        self.colorbar._axis.title = new

    @on_trait_change('colormap')
    def new_colormap(self, new):
        self._cmap = color_map_name_dict[new]
        for plots in self.plot.plots.itervalues():
            for plot in plots:
                if isinstance(plot,ImagePlot) or\
                    isinstance(plot,CMapImagePlot) or\
                    isinstance(plot,ContourPolyPlot):
                    value_range = plot.color_mapper.range
                    plot.color_mapper = self._cmap(value_range)
                    self.plot.color_mapper = self._cmap(value_range)

        self.container.request_redraw()

    #@on_trait_change('x_axis_formatter', dispatch = 'ui')
    def new_x_axis_format(self):
        self.plot.x_axis._invalidate()
        self.plot.invalidate_and_redraw()

    #@on_trait_change('y_axis_formatter', dispatch = 'ui')
    def new_y_axis_format(self):
        self.plot.y_axis._invalidate()
        self.plot.invalidate_and_redraw()

    #@on_trait_change('y_axis_formatter', dispatch = 'ui')
    def new_c_axis_format(self):
        self.colorbar._axis._invalidate()
        self.plot.invalidate_and_redraw()

    def update_plots_index(self, data_c = None):
        if 'c' in self.data.list_data():
            if data_c is not None:
                array = data_c
            else:
                array = self.data.get_data('c')
            xs = linspace(self.x_min, self.x_max, array.shape[1] + 1)
            ys = linspace(self.y_min, self.y_max, array.shape[0] + 1)
            self.plot.range2d.remove(self.plot.index)
            self.plot.index = GridDataSource(xs, ys,
                                        sort_order=('ascending', 'ascending'))
            self.plot.range2d.add(self.plot.index)
            for plots in self.plot.plots.itervalues():
                for plot in plots:
                    plot.index = GridDataSource(xs, ys,
                                        sort_order=('ascending', 'ascending'))

class AutoPlotter2D(Plotter2D):

    def __init__(self, **kwargs):
        super(AutoPlotter2D, self).__init__(**kwargs)
        self.on_trait_change(self.auto_plot_data, 'data:data_changed',
                             dispatch = 'ui')

    #@on_trait_change('data:data_changed', dispacth = 'ui')
    def auto_plot_data(self,new):

        if new.has_key("removed"):
            aux = []
            for deleted in new['removed']:
                aux.append(deleted)
                if deleted+'c' in self.plot.plots.keys():
                    aux.append(deleted+'c')
            self.plot.delplot(*tuple(aux))


        if new.has_key("added"):
            aux = []
            for added in new['added']:
                self.plot.img_plot((added),\
                                    name = added,
                                    colormap = self._cmap,
                                    xbounds = (self.x_min,self.x_max),
                                    ybounds = (self.y_min,self.y_max),
                                )

                if self.add_contour:
                    self.plot.contour_plot((added),\
                                    name = added+'c',
                                    type = 'line',
                                    xbounds = (self.x_min,self.x_max),
                                    ybounds = (self.x_min,self.x_max),
                                )

        if new.has_key("changed"):
            pass

if __name__ == "__main__":

    plotter = Plotter2D()
    plotter.x_axis_formatter = AxisFormatter('e')
    plotter.y_axis_formatter = AxisFormatter('e')
    plotter.configure_traits()