#===========================================================================
# module : panbar.py
# author : Matthieu DARTIAILH
# purpose : Define the class PanBar adding a pantool to a Chaco plot and 
#           creating a toolbar for it. NB : the tool bar need
#           to be added by hand to the plot View.
# 
#
# last modified on : 2013/02/22
#==========================================================================

# Use qt toolkit rather than wxWidget if another backend has not been set
# first
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig is None:
    ETSConfig.toolkit = "qt4"

# Loading modules 
import os
from traits.api import HasTraits, Button, Bool, Instance
from traitsui.api import View, Group, Item
from pyface.api import ImageResource

from chaco.api import DataView
from chaco.tools.api import PanTool

#Defining search path for icon
path = [os.path.join((os.path.dirname(__file__)).decode('utf8'),'Icon')]

# Class defining a custom pan toolbar for chaco plots 
class PanBar(HasTraits):
    
    #Attribute of the class
    plot = Instance(DataView)
    pan = PanTool()
    panSwitch = Button(label = '', style = 'radio',
                        image = ImageResource('Cursor-Hand-icon.png',
                                            search_path = path),)
    panState = Bool(False)
    
    # Initialisation : the plot shoul get an instance of Plot
    def __init__(self,plot):
        super(PanBar,self).__init__()
        self.plot = plot
    
    # Handler for panSwitch button : enable/disable panning
    def _panSwitch_fired(self):
        if self.panState:
            self.plot.tools.remove(self.pan)
            self.panState = False
        else:
            self.pan = PanTool(self.plot, restrict_to_data = True)
            self.plot.tools.append(self.pan)
            self.panState = True
    
    #Build the 'toolbar' with a border, and the label Pan
    view = View(Group(
                    Item('panSwitch', resizable = False, show_label = False),
                    show_labels = False, orientation = 'horizontal',
                    padding = 0, show_border = True,
                    label = 'Pan'),
                style = 'custom')
        
#Run only when the script is executed alone, display the toolbar with
# all options enabled
if __name__ == "__main__":
    PanBar(plot=None).configure_traits()