# Major library imports
import itertools
import warnings
from numpy import arange, array, ndarray, linspace
from types import FunctionType

# Enthought library imports
from traits.api\
    import Delegate, Dict, Instance, Int, List, Property, Str

from chaco.api\
    import AbstractDataSource, AbstractPlotData, ScatterPlot, LinePlot,\
            LinearMapper, LogMapper, ArrayDataSource, ArrayPlotData,\
            BaseXYPlot, DataView, DataRange1D, GridDataSource, GridMapper,\
            Legend, PlotGrid

class Plot1D(DataView):

#------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The PlotData instance that drives this plot.
    data = Instance(AbstractPlotData)

    # Mapping of data names from self.data to their respective datasources.
    datasources = Dict(Str, Instance(AbstractDataSource))

    #------------------------------------------------------------------------
    # General plotting traits
    #------------------------------------------------------------------------

    # Mapping of plot names to *lists* of plot renderers.
    plots = Dict(Str, List)

    # The default index to use when adding new subplots.
    default_index = Instance(AbstractDataSource)

    # List of colors to cycle through when auto-coloring is requested. Picked
    # and ordered to be red-green color-blind friendly, though should not
    # be an issue for blue-yellow.
    auto_colors = List(["white", "red" , "blue","green", "lightblue",
                        "pink", "silver"])

    # index into auto_colors list
    _auto_color_idx = Int(-1)
    _auto_edge_color_idx = Int(-1)
    _auto_face_color_idx = Int(-1)

    # Mapping of renderer type string to renderer class
    # This can be overriden to customize what renderer type the Plot
    # will instantiate for its various plotting methods.
    renderer_map = Dict(dict(line = LinePlot,
                             scatter = ScatterPlot))

    #------------------------------------------------------------------------
    # Annotations and decorations
    #------------------------------------------------------------------------
    # The legend on the plot.
    legend = Instance(Legend)

    # Convenience attribute for legend.align; can be "ur", "ul", "ll", "lr".
    legend_alignment = Property

    def __init__(self, data=None, grid_color='yellow',  **kwtraits):
        if 'origin' in kwtraits:
            self.default_origin = kwtraits.pop('origin')
        if 'bgcolor' not in kwtraits:
            kwtraits['bgcolor'] = 'black'
        super(Plot1D, self).__init__(**kwtraits)

        self.x_grid.line_color = grid_color
        self.y_grid.line_color = grid_color
        self.padding = (65,10,10,50)

        if data is not None:
            if isinstance(data, AbstractPlotData):
                self.data = data
            elif type(data) in (ndarray, tuple, list):
                self.data = ArrayPlotData(data)
            else:
                raise ValueError, "Don't know how to create PlotData for data" \
                                  "of type " + str(type(data))

        if not self.legend:
            self.legend = Legend(visible=False, align="ur", error_icon="blank",
                                 padding=10, component=self)

        # ensure that we only get displayed once by new_window()
        self._plot_ui_info = None

        return

    def plot(self, data, type="line", name=None, index_scale="linear",
             value_scale="linear", origin=None, **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ==========
        data : string, tuple(string), list(string)
            The data to be plotted. The type of plot and the number of
            arguments determines how the arguments are interpreted:

            one item: (line/scatter)
                The data is treated as the value and self.default_index is
                used as the index.  If **default_index** does not exist, one is
                created from arange(len(*data*))
            two or more items: (line/scatter)
                Interpreted as (index, value1, value2, ...).  Each index,value
                pair forms a new plot of the type specified.

        type : comma-delimited string of "line", "scatter", "cmap_scatter"
            The types of plots to add.
        name : string
            The name of the plot.  If None, then a default one is created
            (usually "plotNNN").
        index_scale : string
            The type of scale to use for the index axis. If not "linear", then
            a log scale is used.
        value_scale : string
            The type of scale to use for the value axis. If not "linear", then
            a log scale is used.
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        styles : series of keyword arguments
            attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.

        Examples
        ========
        ::

            plot("my_data", type="line", name="myplot", color=lightblue)

            plot(("x-data", "y-data"), type="scatter")

            plot(("x", "y1", "y2", "y3"))

        Returns
        =======
        [renderers] -> list of renderers created in response to this call to plot()
        """

        if len(data) == 0:
            return

        if isinstance(data, basestring):
            data = (data,)

        self.index_scale = index_scale
        self.value_scale = value_scale

        # TODO: support lists of plot types
        plot_type = type
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin
        if plot_type in ("line", "scatter"):
            if len(data) == 1:
                if self.default_index is None:
                    # Create the default index based on the length of the first
                    # data series
                    value = self._get_or_create_datasource(data[0],sort_order="ascending")
                    self.default_index = ArrayDataSource(arange(len(value.get_data())),
                                                         sort_order="ascending")
                    self.index_range.add(self.default_index)
                index = self.default_index
            else:
                index = self._get_or_create_datasource(data[0])
                if self.default_index is None:
                    self.default_index = index
                self.index_range.add(index)
                data = data[1:]

            new_plots = []
            simple_plot_types = ("line", "scatter")
            for value_name in data:
                value = self._get_or_create_datasource(value_name)
                self.value_range.add(value)
                if plot_type in simple_plot_types:
                    cls = self.renderer_map[plot_type]
                    # handle auto-coloring request
                    if styles.get("color") == "auto":
                        self._auto_color_idx = \
                            (self._auto_color_idx + 1) % len(self.auto_colors)
                        styles["color"] = self.auto_colors[self._auto_color_idx]
                else:
                    raise ValueError("Unhandled plot type: " + plot_type)

                if self.index_scale == "linear":
                    imap = LinearMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)
                else:
                    vmap = LogMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)

                plot = cls(index=index,
                           value=value,
                           index_mapper=imap,
                           value_mapper=vmap,
                           orientation=self.orientation,
                           origin = origin,
                           **styles)
                self.add(plot)
                new_plots.append(plot)

            self.plots[name] = new_plots

        else:
            raise ValueError("Unknown plot type: " + plot_type)

        return self.plots[name]

    def delplot(self, *names):
        """ Removes the named sub-plots. """

        # This process involves removing the plots, then checking the index range
        # and value range for leftover datasources, and removing those if necessary.

        # Remove all the renderers from us (container) and create a set of the
        # datasources that we might have to remove from the ranges
        deleted_sources = set()
        for renderer in itertools.chain(*[self.plots.pop(name) for name in names]):
            self.remove(renderer)
            deleted_sources.add(renderer.index)
            deleted_sources.add(renderer.value)

        #~ #Go back in the auto-coloring index
        for name in names:
            self._auto_color_idx = \
                            (self._auto_color_idx - 1) % len(self.auto_colors)

        # Cull the candidate list of sources to remove by checking the other plots
        sources_in_use = set()
        for p in itertools.chain(*self.plots.values()):
                sources_in_use.add(p.index)
                sources_in_use.add(p.value)

        unused_sources = deleted_sources - sources_in_use - set([None])

        # Remove the unused sources from all ranges and delete them
        for source in unused_sources:
            if source.index_dimension == "scalar":
                # Try both index and range, it doesn't hurt
                self.index_range.remove(source)
                self.value_range.remove(source)
            elif source.index_dimension == "image":
                self.range2d.remove(source)
            else:
                warnings.warn("Couldn't remove datasource from datarange.")

        #Remove the unused sources from the data sources
        for name in names:
            if self.datasources[name] in unused_sources:
                del self.datasources[name]

        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------



    def _make_new_plot_name(self):
        """ Returns a string that is not already used as a plot title.
        """
        n = len(self.plots)
        plot_template = "plot%d"
        while 1:
            name = plot_template % n
            if name not in self.plots:
                break
            else:
                n += 1
        return name

    def _get_or_create_datasource(self, name, sort_order = 'none'):
        """ Returns the data source associated with the given name, or creates
        it if it doesn't exist.
        """

        if name not in self.datasources:
            data = self.data.get_data(name)

            if type(data) in (list, tuple):
                data = array(data)

            if isinstance(data, ndarray):
                if len(data.shape) == 1:
                    ds = ArrayDataSource(data, sort_order=sort_order)
                else:
                    raise ValueError("Unhandled array shape in creating new plot: " \
                                     + str(data.shape))

            elif isinstance(data, AbstractDataSource):
                ds = data

            else:
                raise ValueError("Couldn't create datasource for data of type " + \
                                 str(type(data)))

            self.datasources[name] = ds

        return self.datasources[name]

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _data_changed(self, old, new):
        if old:
            old.on_trait_change(self._data_update_handler, "data_changed",
                                remove=True, dispatch = 'ui')
        if new:
            new.on_trait_change(self._data_update_handler, "data_changed",
                                dispatch = 'ui')

    def _data_update_handler(self, name, event):
        # event should be a dict with keys "added", "removed", and "changed",
        # per the comments in AbstractPlotData.
        if event.has_key("added"):
            pass

        if event.has_key("removed"):
            pass

        if event.has_key("changed"):
            for name in event["changed"]:

                if self.datasources.has_key(name):
                    if self.datasources[name] in self.index_range.sources:
                        index = self.index_range
                        if (index.low_setting == 'auto' and\
                                        index.high_setting != 'auto'):
                            index.set_high('auto')
                        elif(index.low_setting != 'auto' and\
                                        index.high_setting == 'auto'):
                            index.set_low('auto')

                    if self.datasources[name] in self.value_range.sources:
                        value = self.value_range
                        if (value.low_setting == 'auto' and\
                                        value.high_setting != 'auto'):
                            value.set_high('auto')
                        elif(value.low_setting != 'auto' and\
                                        value.high_setting == 'auto'):
                            value.set_low('auto')

                    source = self.datasources[name]
                    source.set_data(self.data.get_data(name))

    def _plots_items_changed(self, event):
        if self.legend:
            self.legend.plots = self.plots

    def _index_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.index_scale == "linear":
            imap = LinearMapper(range=self.index_range,
                                screen_bounds=self.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
        else:
            imap = LogMapper(range=self.index_range,
                             screen_bounds=self.index_mapper.screen_bounds,
                             stretch_data=self.index_mapper.stretch_data)
        self.index_mapper = imap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.index_scale == "linear":
                    imap = LinearMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
                plot.index_mapper = imap

    def _value_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.value_scale == "linear":
            vmap = LinearMapper(range=self.value_range,
                                screen_bounds=self.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
        else:
            vmap = LogMapper(range=self.value_range,
                             screen_bounds=self.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
        self.value_mapper = vmap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
                else:
                    vmap = LogMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
                plot.value_mapper = vmap


    def _legend_changed(self, old, new):
        self._overlay_change_helper(old, new)
        if new:
            new.plots = self.plots

    def _handle_range_changed(self, name, old, new):
        """ Overrides the DataView default behavior.

        Primarily changes how the list of renderers is looked up.
        """
        mapper = getattr(self, name+"_mapper")
        if mapper.range == old:
            mapper.range = new
        if old is not None:
            for datasource in old.sources[:]:
                old.remove(datasource)
                if new is not None:
                    new.add(datasource)
        range_name = name + "_range"
        for renderer in itertools.chain(*self.plots.values()):
            if hasattr(renderer, range_name):
                setattr(renderer, range_name, new)

    #------------------------------------------------------------------------
    # Property getters and setters
    #------------------------------------------------------------------------

    def _set_legend_alignment(self, align):
        if self.legend:
            self.legend.align = align

    def _get_legend_alignment(self):
        if self.legend:
            return self.legend.align
        else:
            return None