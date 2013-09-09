# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 09:09:45 2013

@author: Matthieu
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import (HasTraits, Bool, Str, on_trait_change, Float, Event, List,
        Instance)

from traitsui.api\
    import (View, UItem, EnumEditor, VGroup, Item, Label, HGroup,
            ListInstanceEditor)


from data_holder\
    import DataHolder
    
from numpy import logical_and

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
                        Label('Select filter column'),
                        UItem('filter_column',
                              editor = EnumEditor(name = 'columns'),
                            ),
                        Label('Select filter value'),
                        UItem('value',
                              editor = EnumEditor(name = 'values'),
                            ),
                        show_border = True,
                        ),
                    )

    def filter_data(self):
        """
        """
        if self.active and\
                self.filter_column is not None and self.value is not None:
            aux = self.data_holder.get_data(self.filter_column)
            mask = (aux == self.value)
            return mask
        else:
            return None

    def filter_update(self):
        """
        """
        if self.active and\
                self.filter_column is not None and self.value is not None:
            filter_update = self.data_holder.get_update(self.filter_column)
            mask = (filter_update == self.value)
            return mask
        else:
            return None

    def update_filter_values(self):
        """
        """
        update = self.data_holder.get_update( self.filter_column)
        set_values = set(self.values)
        set_values.update(set(update))
        list_values = list(set_values)
        list_values.sort()
        self.values = list_values

    @on_trait_change('filter_column')
    def new_filter_column(self):
        """
        """
        if self.filter_column:
            old = self.value
            data = self.data_holder.get_data(self.filter_column)
            list_values = list(set(data))
            list_values.sort()
            self.values = list_values
            if old in list_values:
                self.value = old
            else:
                self.active = False

    @on_trait_change('value, active')
    def _request_replot(self, name, new):
        """
        """
        if self.filter_column is not None and self.value is not None:
            if self.active:
                self.request_replot = {'filter_'+name : new}
            elif not self.active:
                self.request_replot = {'filter_'+name : new}

class DataFilter2DList(HasTraits):
    """
    """
    filter_list = List(Instance(DataFilter2D))
    data_holder = Instance(DataHolder)
    columns = List(Str)
    request_replot = Event

    def __init__(self, *args, **kwargs):
        super(DataFilter2DList, self).__init__(*args, **kwargs)
        self.filter_list = [self._add_filter()]

    def active_filters(self):
        """
        """
        filters = []
        for data_filter in self.filter_list:
            if self.data_filter.active and\
                        self.data_filter.filter_column is not None\
                                and self.data_filter.value is not None:

                filters.append(self.data_filter.filter_column)
        return filters

    def filter_data(self, data_list):
        """
        """
        made_copy = False
        final_mask = None
        for data_filter in self.filter_list:
            mask = data_filter.filter_data()
            if mask is not None:
                if final_mask is None:
                    final_mask = mask
                else:
                    final_mask = logical_and(final_mask, mask)

        if final_mask is not None:
            data_list = [data[final_mask] for data in data_list]
            made_copy = True

        return data_list, made_copy

    def filter_update(self, update_list):
        """
        """
        final_mask = None
        for data_filter in self.filter_list:
            mask = data_filter.filter_update()
            if mask is not None:
                if final_mask is None:
                    final_mask = mask
                else:
                    final_mask = logical_and(final_mask, mask)

        update_list = [data[final_mask] for data in update_list]
        made_copy = True

        return update_list, made_copy

    def update_filter_values(self):
        """
        """
        for data_filter in self.filter_list:
           data_filter.update_filter_values()
           
    @on_trait_change('columns')
    def update_columns_for_filters(self):
        """
        """
        for data_filter in self.filter_list:
            data_filter.columns = self.columns
            data_filter.new_filter_column()

    def default_traits_view(self):
        return View(
                VGroup(
                    UItem('filter_list',
                      editor = ListInstanceEditor(style = 'custom',
                                  item_factory = self._add_filter)),
                  ),
                )

    def _add_filter(self, ui = None):
        """
        """
        return (DataFilter2D(data_holder = self.data_holder,
                             columns = self.columns))

    @on_trait_change('filter_list:request_replot')
    def _request_replot(self, new):
        """
        """
        self.request_replot = new


if __name__ == "__main__":
    DataFilter2D().configure_traits()