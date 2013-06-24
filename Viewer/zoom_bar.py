#===========================================================================
# module : zoombar.py
# author : Matthieu DARTIAILH
# purpose : Define the class ZoomBar adding a zoomtool to a Chaco plot and 
#           creating a customizable toolbar for it. NB : the tool bar need
#           to be added by hand to the view.
# 
#
# last modified on : 2013/02/08
#==========================================================================

# Use qt toolkit rather than wxWidget
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

# Loading modules
import os
from traits.api import HasTraits, Button, Bool, Instance, Str
from traitsui.api import View, Group, Item
from traitsui.group import Orientation
from pyface.api import ImageResource

from chaco.tools.api import ZoomTool
from chaco.api import DataView, ColorBar

#Defining search path for icon
path = [os.path.join((os.path.dirname(__file__)).decode('utf8'),'Icon')]


def zoom_bar(plot, orientation = 'horizontal', **kwtraits):
        
    if orientation is 'vertical':
        return ZoomBar_V(plot, **kwtraits)
    elif orientation is 'horizontal':
        return ZoomBar_H(plot, **kwtraits)

# Class defining a custom zoom toolbar for chaco plots
class ZoomBar(HasTraits):
    
    #Attribute of the class
    zoom = ZoomTool
    zoomBox = Button(label='Box',
                     style = 'toolbar',size = -1)
    zoomX = Button(label='X',
                    style = 'toolbar', width_padding = 0,
                    orientation = 'horizontal')
    zoomY = Button(label='Y',    
                    style = 'toolbar', width_padding = 0,
                    orientation = 'vertical')
    nextZoom = Button(label='Next',
                     image = ImageResource('Button-Next-icon.png',
                                            search_path = path),
                     style = 'toolbar',
                     orientation = 'vertical')
    prevZoom = Button(label='Prev',
                     image = ImageResource('Button-Previous-icon.png',
                                            search_path = path),
                     style = 'toolbar',
                     orientation = 'vertical')
    resetZoom = Button(label='Reset',
                        image = ImageResource('Reset-icon.png',
                                            search_path = path),
                        style = 'toolbar',
                        orientation = 'vertical',
                        )
    wheelZoom = Button(label='Wheel', style = 'radio')
    
    traits_view = View(
                Group(
                    Item('zoomBox', resizable = False,
                        defined_when = 'box'),
                    Item('zoomX', resizable = False, 
                        defined_when = 'x'),
                    Item('zoomY', resizable = False,
                        defined_when = 'y'),
                    Item('prevZoom', resizable = False,
                        defined_when = 'prev'),
                    Item('nextZoom', resizable = False,
                        defined_when = 'next'),
                    Item('resetZoom', resizable = False,
                        defined_when = 'reset'),
                    Item('wheelZoom', resizable = False,
                        defined_when = 'wheel'),
                    show_labels = False,
                    orientation = 'horizontal',
                    padding = 0, 
                    show_border = True,
                    label = 'Zoom',
                    ),
                style = 'custom',
                resizable = True 
                )
    
    # Initialisation : the plot should get an instance of DataView,
    # the other keywords are switches to indicates which button should
    #be displayed
    def __init__(self,plot=None,\
                    box = True, x = False, y = False,\
                    next = True, prev = True,\
                    reset = False, wheel = False,\
                    to_mouse = False):
            
        super(ZoomBar, self).__init__(box=box,x=x,y=y,\
                                        next=next,prev=prev,\
                                        reset=reset,wheel=wheel)
                                        
        if isinstance(plot,DataView):
            self.zoom = ZoomTool(plot, always_on=False)
            plot.overlays.append(self.zoom)
            setattr(self.zoom,'zoom_to_mouse',to_mouse)
            setattr(self.zoom,'enable_wheel',False)
            setattr(self.zoom,'zoom_factor',1.1)
            
        if isinstance(plot,ColorBar):
            self.zoom = ZoomTool(plot, axis="index", tool_mode="range",
                            always_on=True, drag_button="right")
            plot.overlays.append(self.zoom)
    
    # Handler for zoomBox button : enable zoom in box mode
    def _zoomBox_fired(self):
        self.zoom.tool_mode = 'box'
        self.zoom.event_state = 'pre_selecting'
        self.zoom._enabled = True 
    
    # Handler for zoomX button : enable zoom in range mode on x axis
    def _zoomX_fired(self):
        self.zoom.tool_mode= 'range'
        self.zoom.axis = 'index'
        self.zoom.event_state = 'pre_selecting'
        self.zoom._enabled = True
    
    # Handler for zoomY button : enable zoom in range mode on y axis
    def _zoomY_fired(self):
        self.zoom.tool_mode= 'range'
        self.zoom.axis = 'value'
        self.zoom.event_state = 'pre_selecting'
        self.zoom._enabled = True
        
    # Handler for nextZoom button : go to next zoom in history  
    def _nextZoom_fired(self):
        aux = getattr(self.zoom,'_history_index')
        if aux < len(getattr(self.zoom,'_history'))-1:
            setattr(self.zoom,'_history_index',aux+1)
            self.zoom._current_state().apply(self.zoom)
    
    # Handler for nextZoom button : go to previous zoom in history
    def _prevZoom_fired(self):
        aux = getattr(self.zoom,'_history_index')
        if aux > 0:
            getattr(self.zoom,'_history')[aux].revert(self.zoom)
            setattr(self.zoom,'_history_index',aux-1)
        
    # Handler for noZoom button : go back to first view in history
    def _resetZoom_fired(self):
        aux = getattr(self.zoom,'_history_index')
        for state in self.zoom._history[::-1]:
            state.revert(self.zoom)
            if aux > 0:
                aux = setattr(self.zoom,'_history_index',aux-1)
        self.zoom._history = [self.zoom._history[0]]
    
    # Handler for wheelZoom button : enable/disable zoom with 
    #   the mouse wheel
    def _wheelZoom_fired(self):
        if getattr(self.zoom,'enable_wheel'):
            setattr(self.zoom,'enable_wheel',False)
        else:
            setattr(self.zoom,'enable_wheel',True)

class ZoomBar_H(ZoomBar):
                    
    traits_view = View(
                    Group(
                        Item('zoomBox', resizable = False,
                            defined_when = 'box',
                            tooltip = 'select a box to which zoom'),
                        Item('zoomX', resizable = False, 
                            defined_when = 'x',
                            tooltip = 'select x range'),
                        Item('zoomY', resizable = False,
                            defined_when = 'y',
                            tooltip = 'select y range'),
                        Item('prevZoom', resizable = False,
                            defined_when = 'prev',
                            tooltip = 'previous zoom state'),
                        Item('nextZoom', resizable = False,
                            defined_when = 'next',
                            tooltip = 'next zoom state'),
                        Item('resetZoom', resizable = False,
                            defined_when = 'reset',
                            tooltip = 'reset zoom'),
                        Item('wheelZoom', resizable = False,
                            defined_when = 'wheel',
                            tooltip = 'activate zoom on wheel'),
                        show_labels = False,
                        orientation = 'horizontal',
                        padding = 0, 
                        show_border = True,
                        label = 'Zoom',
                        ),
                    style = 'custom',
                    resizable = True 
                    )

class ZoomBar_V(ZoomBar):
    
    traits_view = View(
                    Group(
                        Item('zoomBox', resizable = False,
                            defined_when = 'box',
                            tooltip = 'select a box to which zoom'),
                        Item('zoomX', resizable = False, 
                            defined_when = 'x',
                            tooltip = 'select x range'),
                        Item('zoomY', resizable = False,
                            defined_when = 'y',
                            tooltip = 'select y range'),
                        Item('prevZoom', resizable = False,
                            defined_when = 'prev',
                            tooltip = 'previous zoom state'),
                        Item('nextZoom', resizable = False,
                            defined_when = 'next',
                            tooltip = 'next zoom state'),
                        Item('resetZoom', resizable = False,
                            defined_when = 'reset',
                            tooltip = 'reset zoom'),
                        Item('wheelZoom', resizable = False,
                            defined_when = 'wheel',
                            tooltip = 'activate zoom on wheel'),
                        show_labels = False,
                        orientation = 'vertical',
                        padding = 0, 
                        show_border = True,
                        label = 'Zoom',
                        ),
                    style = 'custom',
                    resizable = True 
                    )
    
# Run only when the script is executed alone, display the toolbar with
# all options enabled
if __name__ == "__main__":
    a = zoom_bar(plot=None,\
                    box = True, x = True, y = True,\
                    next = True, prev = True,\
                    reset = True, wheel = True,\
                    to_mouse = True, orientation = 'horizontal')
    a.configure_traits()