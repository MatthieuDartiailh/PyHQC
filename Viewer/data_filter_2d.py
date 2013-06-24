# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 09:09:45 2013

@author: Matthieu
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Bool, Str, on_trait_change, Float, Event, List,\
        Instance

from traitsui.api\
    import View, UItem, EnumEditor, VGroup, Item, Label, HGroup

from data_holder\
    import DataHolder

class DataFilter2D(HasTraits):
    """
    """

    data_holder = Instance(DataHolder)
    active = Bool(False)
    columns = List(Str)
    filter_column = Str
    values = List
    value = Float
    request_replot = Event

    traits_view = View(
                    VGroup(
                        HGroup(
                            Item('active', label = 'Active'),
                            ),
                        Label('Select column to be used for filtering'),
                        UItem('filter_column',
                              editor = EnumEditor(name = 'columns'),
                            ),
                        Label('Select value to be used for filtering'),
                        UItem('value',
                              editor = EnumEditor(name = 'values'),
                            ),
                        ),
                    )

    def filter_data(self, data_list):
        """
        """
        made_copy = False
        if self.active and\
                self.filter_column is not None and self.value is not None:
            aux = self.data_holder.get_data(self.filter_column)
            mask = (aux == self.value)
            data_list = [data[mask] for data in data_list]
            made_copy = True

        return data_list, made_copy

    def filter_update(self, update_list):
        """
        """
        made_copy = False
        if self.active and\
                self.filter_column is not None and self.value is not None:
            aux = self.data_holder.get_update(self.filter_column)
            mask = (aux == self.value)
            update_list = [update[mask] for update in update_list]
            made_copy = True

        return update_list, made_copy

    @on_trait_change('filter_column')
    def _update_values_from_filter(self, new):
        """
        """
        self.values = list(set(self.data_holder.get_data(new)))

    @on_trait_change('value, active')
    def _request_replot(self, name, new):
        """
        """
        if self.active and\
                self.filter_column is not None and self.value is not None:
            self.request_replot = {'filter_'+name : new}
        elif not self.active:
            self.request_replot = {'filter_'+name : new}

if __name__ == "__main__":
    DataFilter2D().configure_traits()