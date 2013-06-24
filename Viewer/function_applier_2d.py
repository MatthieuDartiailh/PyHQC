# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 21:59:51 2013

@author: Matthieu
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Instance, List, Str, Bool, on_trait_change, Event

from traitsui.api\
    import View, UItem, EnumEditor, VGroup, Item, Label, HGroup

from function_2d\
    import Abstract2DFunction, FUNCTIONS_2D

import function_2d

class FunctionApplier2D(HasTraits):
    """
    """

    active = Bool(False)
    function_list = List(Str, FUNCTIONS_2D)
    selected_function = Str()
    current_function = Instance(Abstract2DFunction)
    request_replot = Event

    trait_view = View(
                    VGroup(
                        HGroup(
                            Item('active',
                                 label = 'Apply ?',
                                 ),
                             ),
                        Label('Select function'),
                        UItem('selected_function',
                              editor = EnumEditor(name = 'function_list'),
                             ),
                        ),
                    )
    def __init__(self, **kwarg):
        super(FunctionApplier2D, self).__init__()
        self.selected_function = FUNCTIONS_2D[0]

    @on_trait_change('selected_function')
    def update_current_function(self, new):
        """
        """
        klass = getattr(function_2d, new)
        self.current_function = klass()
        self.request_replot = {'new_function' : True}

    def process(self, data):
        """
        """
        if self.active:
            return self.current_function.process(data)
        else:
            return data

    def pre_update(self, data):
        """
        """
        if self.active:
            return self.current_function.pre_update(data)
        else:
            return data

    def update(self, data):
        """
        """
        if self.active:
            return self.current_function.update(data)
        else:
            return data

    def _active_changed(self, new):
        """
        """
        print 'function_applier 2d active changed'
        self.request_replot = {'active' : new}

if __name__ == "__main__":
    FunctionApplier2D().configure_traits()