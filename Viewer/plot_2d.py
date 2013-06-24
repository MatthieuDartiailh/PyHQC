""" Defines the Plot class.
"""
# Major library imports
import itertools
import warnings
from numpy import arange, array, ndarray, linspace
from types import FunctionType

# Enthought library imports
from traits.api import Delegate, Dict, Instance, Int, List, Property, Str

from chaco.api\
    import AbstractDataSource, AbstractPlotData,\
            LinearMapper, LogMapper, ArrayDataSource, ArrayPlotData,\
            DataView, DataRange1D, GridDataSource, GridMapper,\
            Legend, PlotGrid,ImagePlot,ImageData,CMapImagePlot,\
            ContourPolyPlot,ContourLinePlot

from chaco.abstract_colormap\
    import AbstractColormap

class Plot2D(DataView):

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

    index2d = Instance(GridDataSource)

    # Optional mapper for the color axis.  Not instantiated until first use;
    # destroyed if no color plots are on the plot.
    color_mapper = Instance(AbstractColormap)

    # Mapping of renderer type string to renderer class
    # This can be overriden to customize what renderer type the Plot
    # will instantiate for its various plotting methods.
    renderer_map = Dict(dict(img_plot = ImagePlot,
                             cmap_img_plot = CMapImagePlot,
                             contour_line_plot = ContourLinePlot,
                             contour_poly_plot = ContourPolyPlot,
                             ))

    #------------------------------------------------------------------------
    # Annotations and decorations
    #------------------------------------------------------------------------

    # The legend on the plot.
    legend = Instance(Legend)

    # Convenience attribute for legend.align; can be "ur", "ul", "ll", "lr".
    legend_alignment = Property

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, data=None, **kwtraits):
        if 'origin' in kwtraits:
            self.default_origin = kwtraits.pop('origin')
        if 'bgcolor' not in kwtraits:
            kwtraits['bgcolor'] = 'black'
            
        super(Plot2D, self).__init__(**kwtraits)
        
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

    def img_plot(self, data, name=None, colormap=None,
                 xbounds=None, ybounds=None, origin=None, hide_grids=True, **styles):
        """ Adds image plots to this Plot object.

        If *data* has shape (N, M, 3) or (N, M, 4), then it is treated as RGB or
        RGBA (respectively) and *colormap* is ignored.

        If *data* is an array of floating-point data, then a colormap can
        be provided via the *colormap* argument, or the default of 'Spectral'
        will be used.

        *Data* should be in row-major order, so that xbounds corresponds to
        *data*'s second axis, and ybounds corresponds to the first axis.

        Parameters
        ==========
        data : string
            The name of the data array in self.plot_data
        name : string
            The name of the plot; if omitted, then a name is generated.
        xbounds, ybounds : string, tuple, or ndarray
            Bounds where this image resides. Bound may be: a) names of
            data in the plot data; b) tuples of (low, high) in data space,
            c) 1D arrays of values representing the pixel boundaries (must
            be 1 element larger than underlying data), or
            d) 2D arrays as obtained from a meshgrid operation
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        hide_grids : bool, default True
            Whether or not to automatically hide the grid lines on the plot
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        value = self._get_or_create_datasource(data)
        array_data = value.get_data()
        if len(array_data.shape) == 3:
            if array_data.shape[2] not in (3,4):
                raise ValueError("Image plots require color depth of 3 or 4.")
            cls = self.renderer_map["img_plot"]
            kwargs = dict(**styles)
        else:
            if colormap is None:
                if self.color_mapper is None:
                    colormap = Spectral(DataRange1D(value))
                else:
                    colormap = self.color_mapper
            elif isinstance(colormap, AbstractColormap):
                if colormap.range is None:
                    colormap.range = DataRange1D(value)
            else:
                colormap = colormap(DataRange1D(value))
            self.color_mapper = colormap
            cls = self.renderer_map["cmap_img_plot"]
            kwargs = dict(value_mapper=colormap, **styles)
        return self._create_2d_plot(cls, name, origin, xbounds, ybounds, value,
                                    hide_grids, **kwargs)


    def contour_plot(self, data, type="line", name=None, poly_cmap=None,
                     xbounds=None, ybounds=None, origin=None, hide_grids=True, **styles):
        """ Adds contour plots to this Plot object.

        Parameters
        ==========
        data : string
            The name of the data array in self.plot_data, which must be
            floating point data.
        type : comma-delimited string of "line", "poly"
            The type of contour plot to add. If the value is "poly"
            and no colormap is provided via the *poly_cmap* argument, then
            a default colormap of 'Spectral' is used.
        name : string
            The name of the plot; if omitted, then a name is generated.
        poly_cmap : string
            The name of the color-map function to call (in
            chaco.default_colormaps) or an AbstractColormap instance
            to use for contour poly plots (ignored for contour line plots)
        xbounds, ybounds : string, tuple, or ndarray
            Bounds where this image resides. Bound may be: a) names of
            data in the plot data; b) tuples of (low, high) in data space,
            c) 1D arrays of values representing the pixel boundaries (must
            be 1 element larger than underlying data), or
            d) 2D arrays as obtained from a meshgrid operation
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        hide_grids : bool, default True
            Whether or not to automatically hide the grid lines on the plot
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        value = self._get_or_create_datasource(data)
        if value.value_depth != 1:
            raise ValueError("Contour plots require 2D scalar field")
        if type == "line":
            cls = self.renderer_map["contour_line_plot"]
            kwargs = dict(**styles)
            # if colors is given as a factory func, use it to make a
            # concrete colormapper. Better way to do this?
            if "colors" in kwargs:
                cmap = kwargs["colors"]
                if isinstance(cmap, FunctionType):
                    kwargs["colors"] = cmap(DataRange1D(value))
                elif getattr(cmap, 'range', 'dummy') is None:
                    cmap.range = DataRange1D(value)
        elif type == "poly":
            if poly_cmap is None:
                poly_cmap = Spectral(DataRange1D(value))
            elif isinstance(poly_cmap, FunctionType):
                poly_cmap = poly_cmap(DataRange1D(value))
            elif getattr(poly_cmap, 'range', 'dummy') is None:
                poly_cmap.range = DataRange1D(value)
            cls = self.renderer_map["contour_poly_plot"]
            kwargs = dict(color_mapper=poly_cmap, **styles)
        else:
            raise ValueError("Unhandled contour plot type: " + type)

        return self._create_2d_plot(cls, name, origin, xbounds, ybounds, value,
                                    hide_grids, **kwargs)


    def _process_2d_bounds(self, bounds, array_data, axis):
        """Transform an arbitrary bounds definition into a linspace.

        Process all the ways the user could have defined the x- or y-bounds
        of a 2d plot and return a linspace between the lower and upper
        range of the bounds.

        Parameters
        ----------
        bounds : any
            User bounds definition

        array_data : 2D array
            The 2D plot data

        axis : int
            The axis along which the bounds are tyo be set
        """

        num_ticks = array_data.shape[axis] + 1

        if bounds is None:
            return arange(num_ticks)

        if type(bounds) is tuple:
            # create a linspace with the bounds limits
            return linspace(bounds[0], bounds[1], num_ticks)

        if type(bounds) is ndarray and len(bounds.shape) == 1:
            # bounds is 1D, but of the wrong size

            if len(bounds) != num_ticks:
                msg = ("1D bounds of an image plot needs to have 1 more "
                       "element than its corresponding data shape, because "
                       "they represent the locations of pixel boundaries.")
                raise ValueError(msg)
            else:
                return linspace(bounds[0], bounds[-1], num_ticks)

        if type(bounds) is ndarray and len(bounds.shape) == 2:
            # bounds is 2D, assumed to be a meshgrid
            # This is triggered when doing something like
            # >>> xbounds, ybounds = meshgrid(...)
            # >>> z = f(xbounds, ybounds)

            if bounds.shape != array_data.shape:
                msg = ("2D bounds of an image plot needs to have the same "
                       "shape as the underlying data, because "
                       "they are assumed to be generated from meshgrids.")
                raise ValueError(msg)
            else:
                if axis == 0: bounds = bounds[:,0]
                else: bounds = bounds[0,:]
                interval = bounds[1] - bounds[0]
                return linspace(bounds[0], bounds[-1]+interval, num_ticks)

        raise ValueError("bounds must be None, a tuple, an array, "
                         "or a PlotData name")


    def _create_2d_plot(self, cls, name, origin, xbounds, ybounds, value_ds,
                        hide_grids, **kwargs):
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        array_data = value_ds.get_data()

        #~ # process bounds to get linspaces
        if isinstance(xbounds, basestring):
            xbounds = self._get_or_create_datasource(xbounds).get_data()

        xs = self._process_2d_bounds(xbounds, array_data, 1)

        if isinstance(ybounds, basestring):
            ybounds = self._get_or_create_datasource(ybounds).get_data()

        ys = self._process_2d_bounds(ybounds, array_data, 0)

        # Create the index and add its datasources to the appropriate ranges
        self.index = GridDataSource(xs, ys, sort_order=('ascending', 'ascending'))
        self.range2d.add(self.index)
        mapper = GridMapper(range=self.range2d,
                            stretch_data_x=self.x_mapper.stretch_data,
                            stretch_data_y=self.y_mapper.stretch_data)

        plot = cls(index=self.index,
                   value=value_ds,
                   index_mapper=mapper,
                   orientation=self.orientation,
                   origin=origin,
                   **kwargs)

        if hide_grids:
            self.x_grid.visible = False
            self.y_grid.visible = False

        self.add(plot)
        self.plots[name] = [plot]
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

        # Cull the candidate list of sources to remove by checking the other plots
        sources_in_use = set()
        for p in itertools.chain(*self.plots.values()):
                sources_in_use.add(p.index)
                sources_in_use.add(p.value)

        unused_sources = deleted_sources - sources_in_use - set([None])

        # Remove the unused sources from all ranges
        for source in unused_sources:
            if source.index_dimension == "scalar":
                # Try both index and range, it doesn't hurt
                self.index_range.remove(source)
                self.value_range.remove(source)
            elif source.index_dimension == "image":
                self.range2d.remove(source)
            else:
                warnings.warn("Couldn't remove datasource from datarange.")

        return

    def hideplot(self, *names):
        """ Convenience function to sets the named plots to be invisible.  Their
        renderers are not removed, and they are still in the list of plots.
        """
        for renderer in itertools.chain(*[self.plots[name] for name in names]):
            renderer.visible = False
        return

    def showplot(self, *names):
        """ Convenience function to sets the named plots to be visible.
        """
        for renderer in itertools.chain(*[self.plots[name] for name in names]):
            renderer.visible = True
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
                elif len(data.shape) == 2:
                    ds = ImageData(data=data, value_depth=1)
                elif len(data.shape) == 3:
                    if data.shape[2] in (3,4):
                        ds = ImageData(data=data, value_depth=int(data.shape[2]))
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

    def _color_mapper_changed(self):
        for plist in self.plots.values():
            for plot in plist:
                plot.color_mapper = self.color_mapper
        self.invalidate_draw()

    def _data_changed(self, old, new):
        if old:
            old.on_trait_change(self._data_update_handler, "data_changed",
                                remove=True)
        if new:
            new.on_trait_change(self._data_update_handler, "data_changed")

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
                    source = self.datasources[name]
                    source.set_data(self.data.get_data(name))

    def _plots_items_changed(self, event):
        if self.legend:
            self.legend.plots = self.plots

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
