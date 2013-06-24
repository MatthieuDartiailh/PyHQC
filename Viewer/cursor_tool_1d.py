# Use qt toolkit rather than wxWidget if another backend has not been set
# first
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"


from traits.api\
    import Float, Str, Bool, HasTraits, Color,\
                            on_trait_change, Instance, Button
from traitsui.api\
    import View, HGroup, Item, UItem, VGroup, RangeEditor, Handler
    
from chaco.tools.cursor_tool\
    import BaseCursorTool
    
from chaco.api\
    import DataView

import numpy

from float_display\
    import FloatDisplay

class CursorTool1D_(BaseCursorTool):

    #The current index-value of the cursor
    current_index = Float(0)
    current_value = Float(0)

    #if true, draws a line parallel to the index-axis
    #through the cursor intersection point
    show_value_line = Bool(True)

    def _current_index_changed(self):
        self.component.request_redraw()
        
    def _current_value_changed(self):
        self.component.request_redraw()

    def _get_current_position(self):
        x = self.current_index
        y = self.current_value
        return x,y

    def _set_current_position(self, traitname, args):
        plot = self.component
        if args[0] < plot.index_range.low:
            self.current_index = plot.index_range.low
        elif args[0] > plot.index_range.high:
            self.current_index = plot.index_range.high
        else:
            self.current_index = args[0]
            
        if args[1] < plot.value_range.low:
            self.current_value = plot.value_range.low
        elif args[1] > plot.value_range.high:
            self.current_value = plot.value_range.high
        else:
            self.current_value = args[1]

    def draw(self, gc, view_bounds=None):
        """ Draws this tool on a graphics context.

        Overrides LineInspector, BaseTool.
        """
        # We draw at different points depending on whether or not we are
        # interactive.  If both listener and interactive are true, then the
        # selection metadata on the plot component takes precendence.
        plot = self.component
        if plot is None:
            return

        sx, sy = plot.map_screen(self.current_position)
        orientation = plot.orientation

        if orientation == "h" and sx is not None:
            self._draw_vertical_line(gc, sx)
        elif sy is not None:
            self._draw_horizontal_line(gc, sy)

        if self.show_marker:
            self._draw_marker(gc, sx, sy)

        if self.show_value_line:
            if orientation == "h" and sy is not None:
                self._draw_horizontal_line(gc, sy)
            elif sx is not None:
                self._draw_vertical_line(gc, sx)

    def is_draggable(self, x, y):
        plot = self.component
        if plot is not None:
            orientation = plot.orientation
            sx, sy = plot.map_screen(self.current_position)
            if orientation=='h' and numpy.abs(sx-x) <= self.threshold:
                return True
            elif orientation=='v' and numpy.abs(sy-y) <= self.threshold:
                return True
        return False

    def dragging(self, event):
        x,y = event.x, event.y
        plot = self.component
        ndx, ndy = plot.map_data((x, y))
        if ndx is None or ndy is None:
            return
            
        if ndx < plot.index_range.low:
            self.current_index = plot.index_range.low
        elif ndx > plot.index_range.high:
            self.current_index = plot.index_range.high
        else:
            self.current_index = ndx
            
        if ndy < plot.value_range.low:
            self.current_value = plot.value_range.low
        elif ndy > plot.value_range.high:
            self.current_value = plot.value_range.high
        else:
            self.current_value = ndy

class CursorTool1D(Handler):
    
    name = Str('Cursor')
    selected = Bool(False)
    index = Instance(FloatDisplay,())
    value = Instance(FloatDisplay,())
    cursor = Instance(CursorTool1D_)
    color = Color('red')
    prop = Button(type = 'toolbar', label = 'P')
    
    trait_view = View(HGroup(
                    Item('index', style = 'custom', label = 'X'),
                    Item('value', style = 'custom', label = 'Y'),
                    Item('prop', style = 'custom', width = -30)
                    )
                )
        
    bar_view = View(HGroup(
                    UItem('selected'),
                    UItem('name'),
                    Item('index', style = 'custom', label = 'X'),
                    Item('value', style = 'custom', label = 'Y'),
                    Item('prop', style = 'custom', width = -30)
                    )
                )
    
    def __init__(self, plot, name = 'Cursor', color = 'red'):
        super(CursorTool1D,self).__init__(name = name)
        
        if isinstance(plot,DataView):
            self.cursor = CursorTool1D_(plot,drag_button="left",
                                    color = color)
            plot.overlays.append(self.cursor)
            self.cursor.component.request_redraw()
            
            self.cursor.on_trait_change(self.update_index,'current_index')
            self.cursor.on_trait_change(self.update_value,'current_value')
        else:
            print "Incorrect type of plot for CursorTool1D"
        
        self.color = color
        
    
    @on_trait_change('cursor.current_index')
    def update_index(self,name,new):
        self.index.value = new
        
    @on_trait_change('cursor.current_value')
    def update_value(self,name,new):
        self.value.value = new
        
    @on_trait_change('color')
    def update_color(self, name, new):
        self.cursor.color = new
        
    @on_trait_change('index.user_input')
    def user_index(self, name, new):
        self.cursor.current_position = new, self.value.value
        
    @on_trait_change('value.user_input')
    def user_value(self, name, new):
        self.cursor.current_position = self.index.value, new
        
    def object_prop_changed(self,info):
        prop_view = View(VGroup(
                        Item('color', label = 'Cursor color'),
                        HGroup(
                            VGroup(
                                Item('object.index.format_enum',
                                        label = 'Format'),
                                Item('object.index.digits',
                                        label = 'Digits'),
                                show_border = True,
                                label = 'X'),
                            VGroup(
                                Item('object.value.format_enum',
                                        label = 'Format'),
                                Item('object.value.digits',
                                        label = 'Digits'),
                                show_border = True,
                                label = 'Y'),
                            )
                        ),
                    title = self.name,
                    kind = 'livemodal')
        
        self.edit_traits(view = prop_view, parent = info.ui.control)

if __name__ == "__main__":
    CursorTool1D(None).configure_traits()