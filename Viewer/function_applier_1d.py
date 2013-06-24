# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 17:35:02 2013

@author: Matthieu
"""

from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Instance, List, Str, Bool, on_trait_change, Event

from traitsui.api\
    import View, UItem, EnumEditor, VGroup, Item, Label, HGroup

from function_1d\
    import Abstract1DFunction, FUNCTIONS_1D

import function_1d

class FunctionApplier1D(HasTraits):
    """
    """

    active = Bool(False)
    function_list = List(Str, FUNCTIONS_1D)
    selected_function = Str(FUNCTIONS_1D[0])
    current_functions = List(Instance(Abstract1DFunction))
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
        super(FunctionApplier1D, self).__init__(**kwarg)

    @on_trait_change('selected_function')
    def update_current_function(self):
        """
        """
        self.current_functions = []
        self.request_replot = {'new_function' : True}

    def process(self, data_list):
        """
        """
        if self.active:
            klass = getattr(function_1d, self.selected_function)
            while len(self.current_functions) < len(data_list):
                self.current_functions.append(klass())
            while len(self.current_functions) > len(data_list):
                del self.current_functions[-1]

            return [self.current_functions[i].process(data_list[i]) \
                    for i in xrange(len(data_list))]
        else:
            return data_list

    def update(self, update_list):
        """
        """
        if self.active:
            return [self.current_functions[i].process(update_list[i]) \
                    for i in xrange(len(update_list))]
        else:
            return update_list

    def _active_changed(self, new):
        """
        """
        self.request_replot = {'active' : new}

if __name__ == "__main__":
    FunctionApplier1D().configure_traits()