from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, List, Str, Instance, Int, Float,\
            Bool, Button, Tuple, Any, Range, Event,\
            on_trait_change

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Handler,\
            Spring, EnumEditor, ListStrEditor, Group,\
            ButtonEditor

from pyface.api\
    import FileDialog, OK

from chaco.api\
    import  DataView, BasePlotContainer, ColorBar

class SaveGraphBarHandler(Handler):

    def object_dialog_button_changed(self, info)
        info.object.edit_traits(view = object.trait_view(name = 'dialog'),
                                parent  = info.ui.control)


class SaveGraphBar(HasTraits):

    plot = Instance(DataView)
    container = Instance(BasePlotContainer)
    colorbar = Instance(ColorBar)
    padding_left = Range(0,200)
    padding_right = Range(0,200)
    padding_top = Range(0,200)
    padding_bottom = Range(0,200)
    colorbar_width = Range(0,100)
    auto_update = Bool(True)
    dialog_button = Button(label = 'Save plot')
    save_button = Button(label = 'Save')
    
    traits_view = View(
                    Group(
                        UItem('save_button'),
                        show_border = True,
                        ),
                    handler = SaveGraphBarHandler()
                    )
                    
    dialog = View(
                    
                

    def __init__(self, plot = None, container = None, colorbar = None):
        super(SaveGraphBar, self).__init__()
        
        if plot is not None:
            self.plot = plot
            self.sync_trait('padding_left',plot)
            self.sync_trait('padding_right',plot)
            self.sync_trait('padding_top',plot)
            self.sync_trait('padding_bottom',plot)
        else:
            print 'SaveGraphBar instance need at least a DataView instance\
                to work properly'
                
        if container is not None:
            self.container = container
            
        if colorbar is not None:
            self.colorbar = colorbar
            self.sync_trait('colorbar_width',colorbar,alias = 'width')
                
    @on_trait_change('save_button')
    def save_graph(self):
                    