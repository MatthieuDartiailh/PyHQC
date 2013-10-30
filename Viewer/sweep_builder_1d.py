"""
"""

from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import (HasTraits, List, Str, Instance, Int, Float,  Bool, Range,
            on_trait_change, Event, Array)

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Spring, EnumEditor,\
        Group, TextEditor

from data_holder import DataHolder
from data_filter import DataFilterList

from numpy\
    import concatenate, lexsort, array


class SweepBuilder1D(HasTraits):
    """
    """

    show_all = Bool(True)
    columns = List(Str)
    sweep_column = Str

    sweep_size = Int(5)
    sweep_start_index = Range(low = '_sweep_start_min_index',
                              high = '_sweep_start_max_index', value = 0,
                              mode = 'spinner')
    sweep_stop_index = Range(low = '_sweep_stop_min_index',
                             high = '_sweep_stop_max_index', value = 1,
                             mode = 'spinner')

    sweep_start_value = Float(0.5)
    sweep_stop_value = Float(1.0)
    sweep_step_value = Float(1.0)
    sweep_min_value = Float(0.5)

    request_replot = Event

    _data_holder = Instance(DataHolder)
    _data_filter = Instance(DataFilterList)
    _allow_update = Bool(True)
    _mask = Array
    _map = Array

    _sweep_start_min_index = Int(0)
    _sweep_start_max_index = Int(4)
    _sweep_start_value = Float
    _sweep_stop_min_index = Int(1)
    _sweep_stop_max_index = Int(5)

    traist_view = View(
                     VGroup(
                        HGroup(Spring(),
                            Item('show_all', emphasized = True,
                                 enabled_when = "sweep_column != ''"),
                            Spring()),
                        HGroup(Spring(),
                            Group(
                                UItem('sweep_column',
                                    editor = EnumEditor(name = 'columns'),
                                    width = 150),
                                label = 'Sweep column',
                                ),
                            Spring(),
                            ),
                        HGroup(Spring(),
                            VGroup(
                                Item('sweep_start_index', label = 'Start'),
                                Item('sweep_stop_index', label = 'Stop'),
                                label = 'Index',
                                ),
                            VGroup(
                                UItem('sweep_start_value',
                                    editor = TextEditor(auto_set = False,
                                                        enter_set = True,
                                                        evaluate = float),
                                    ),
                                UItem('sweep_stop_value',
                                    editor = TextEditor(auto_set = False,
                                                        enter_set = True,
                                                        evaluate = float),
                                    ),
                                label = 'Value'
                                ),
                            Spring(),
                            ),
                        ),
                    )

    def __init__(self, data_holder, data_filter, **kwarg):

        super(SweepBuilder1D, self).__init__(**kwarg)
        self._data_holder = data_holder
        self._data_filter = data_filter

    def build_sweep(self, data_list, new_x = True):
        """
        """
        made_copy = False
        if self.show_all :
            return data_list, made_copy

        if new_x:
            sweep = self._data_holder.get_data(self.sweep_column)
            sweep = self._data_filter.filter_data([sweep])[0][0]
            self._mask = array((self._sweep_start_value <= sweep) & \
                                            (sweep < self._sweep_stop_value))
            masked_sweep = sweep[self._mask]
            masked_x = data_list[0][self._mask]
            self._map = lexsort((masked_x, masked_sweep))

        made_copy = True
        return [data[self._mask][self._map] for data in data_list], made_copy

#        if self.mode == 'contiguous':
#            start = self.sweep_size*(self.sweep_start_index-1)
#            stop  = self.sweep_size*(self.sweep_stop_index-1)
#            #This is safe for numpy array no matter the stop value
#            return [ data[start:stop] for data in data_list], made_copy
#        else:
#            made_copy = True
#            sweep = self._data_holder.get_data(self.sweep_column)
#            start = self.sweep_start_value
#            stop = self.sweep_stop_value
#            length = (stop - start)/self.sweep_step_value
#            values = linspace(start, stop, length)
#            masks = [(sweep == value) for value in values]
#            return [concatenate([data[mask] for mask in masks])\
#                        for data in data_lis_sweep_start_valuet], made_copy

    def update_sweep(self, sweep_update, update_list, plot_data_list):
        """
        """
        raw_data = False
        if self.show_all :
            return [concatenate((plot_data_list[i], update_list[i]))\
                for i in xrange(len(update_list))], raw_data

        mask = \
            array((self._sweep_start_value <= sweep_update) & \
                                        (sweep_update < self._sweep_stop_value))
        if any(mask):
            self._mask = concatenate((self._mask, mask))
            sweep = self._data_holder.get_data(self.sweep_column)
            [sweep], copy = self._data_filter.filter_data([sweep])
            masked_sweep = sweep[self._mask]
            masked_x = \
                concatenate((plot_data_list[0], update_list[0][mask]))
            self._map = lexsort((masked_x, masked_sweep))

            for i in xrange(len(plot_data_list)):
                plot_data_list[i] = concatenate((plot_data_list[i],
                    update_list[i][mask]))[self._map]

        return plot_data_list, raw_data


#        if self.mode == 'contiguous' :
#            stop = self.sweep_size*(self.sweep_stop_index-1)
#            start = self.sweep_size*(self.sweep_start_index-1)
#            available_length = stop - start - len(plot_data_list[0])
#            if available_length >= 0:
#                for i in xrange(len(plot_data_list)):
#                    plot_data_list[i] = concatenate((plot_data_list[i],
#                    update_list[i][0:available_length]))
#
#                return plot_data_list, raw_data
#
#            else:
#                return plot_data_list, raw_data
#
#        elif self.mode == 'periodic' :
#            sweep_update = self._data_holder.get_update(self.sweep_column)
#            start = self.sweep_start_value
#            stop = self.sweep_stop_value
#            length = (stop - start)/self.sweep_step_value
#            values = linspace(start, stop, length).tolist()
#            for i, value in enumerate(sweep_update):
#                if value in values:
#                    period_index = values.index(value)
#                    for j in xrange(len(plot_data_list)):
#                        plot_data_list[j] = insert(plot_data_list[j],
#                                    (period_index+1)*self.sweep_period + i,
#                                    update_list[j][i])
#
#            return plot_data_list, raw_data
#
#        else:
#            #Here we will always return a copy, which is equivalent to raw_data
#            # is True
#            return self.filter_data(data_list)

    def refresh_sweep_data(self):
        """
        """
        dat = sorted(set(self._data_holder.get_data(self.sweep_column)))
        if len(dat) > 1:
            self.sweep_size = len(dat)
            self.sweep_min_value = min(dat)
            self.sweep_step_value = dat[1]-dat[0]
        else:
            self.show_all = True

    @on_trait_change('show_all')
    def switch_show_all(self, new):
        """
        """
        self._ask_replot('show_all', new)

        self.on_trait_change(self._ask_replot,
                            'sweep_start_index',remove = new)

        self.on_trait_change(self._ask_replot,
                            'sweep_stop_index',remove = new)

        self.on_trait_change(self._ask_replot,
                            'sweep_start_value',remove = new)

        self.on_trait_change(self._ask_replot,
                            'sweep_stop_value',remove = new)

    def _ask_replot(self, name, new):
        """
        """
        self.request_replot = {'sweep' : name}

    @on_trait_change('sweep_column')
    def _new_sweep_column(self, new):
        """
        """
        dat = sorted(set(self._data_holder.get_data(new)))
        if len(dat) > 1:
            self.sweep_size = len(dat)
            self.sweep_min_value = min(dat)
            self.sweep_step_value = dat[1]-dat[0]
        else:
            self.show_all = True

        self.sweep_start_index = 0
        self._new_start_index(0)
        self.sweep_stop_index = 1
        self._new_stop_index(1)

#        ref = dat[0]
#        size = 1
#        while ref == dat[size] and size < len(dat):
#            size += 1
#
#        self.sweep_size = size
#
#        if size > 1:
#            self.mode = 'contiguous'
#            self.sweep_min_value = ref
#            if len(dat) > self.sweep_size:
#                self.sweep_step_value = dat[self.sweep_size]-ref
#        else:
#            set_dat = set(dat)
#            self.sweep_min_value = min(set_dat)
#            self.sweep_step_value = \
#                (max(set_dat)-self.sweep_min_value)/(len(set_dat)-1)
#            if len(dat) > len(set_dat):
#                if ref == dat[len(set_dat)]:
#                    self.mode = 'periodic'
#                    self.sweep_period = len(set_dat)
#            else:
#                self.mode = 'sort'
#
#        print 'sweep_builder new_sweep column mode : {}'.format(self.mode)
#        self.sweep_start_value = ref +\
#                    (self.sweep_start_index-1)*self.sweep_step_value
#        self.sweep_stop_value = ref +\
#                    (self.sweep_stop_index-1)*self.sweep_step_value


    @on_trait_change('sweep_start_index')
    def _new_start_index(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            aux = self.sweep_min_value + new*self.sweep_step_value
            self.sweep_start_value = aux
            if new > self.sweep_stop_index-1:
                self.sweep_stop_index = new + 1
                aux = self.sweep_min_value + (new + 1)*self.sweep_step_value
                self.sweep_stop_value = aux
            self._allow_update = True

    @on_trait_change('sweep_stop_index')
    def _new_stop_index(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            aux = self.sweep_min_value + new*self.sweep_step_value
            self.sweep_stop_value = aux
            if new < self.sweep_start_index+1:
                self.sweep_start_index = new-1
                aux = self.sweep_min_value + (new-1)*self.sweep_step_value
                self.sweep_start_value = aux
            self._allow_update = True

    @on_trait_change('sweep_start_value')
    def _new_start_value(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            index = int(round((new - self.sweep_min_value)/ \
                                                self.sweep_step_value)) + 1
            if index >= 0 and index < self.sweep_size:
                self.sweep_start_index = index

                if index > self.sweep_stop_index - 1:
                    self.sweep_stop_index = index + 1
                    self.sweep_stop_value = self.sweep_min_value +\
                                            (index)*self.sweep_step_value
            elif index < 0:
                self.sweep_start_index = 0
                self.sweep_start_value = self.sweep_min_value

            else:
                self.sweep_start_index = self.sweep_size-1
                self.sweep_start_value = self.sweep_min_value +\
                                (self.sweep_size - 1)*self.sweep_step_value
            self._allow_update = True

    @on_trait_change('sweep_stop_value')
    def _new_stop_value(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            index = int(round((new - self.sweep_min_value)/ \
                                            self.sweep_step_value)) + 1
            if index > 0 and index < self.sweep_size+1:
                self.sweep_stop_index = index

                if index < self.sweep_start_index + 1:
                    self.sweep_start_index = index - 1
                    aux = self.sweep_min_value +\
                                (index - 1)*self.sweep_step_value
                    self.sweep_start_value = aux

            elif index < 1:
                self.sweep_stop_index = 1
                self.sweep_stop_value = self.sweep_min_value +\
                                            self.sweep_step_value
            else:
                self.sweep_stop_index = self.sweep_size
                self.sweep_stop_value = self.sweep_min_value +\
                                        self.sweep_size*self.sweep_step_value
            self._allow_update = True

    def _sweep_size_changed(self, new):
        """
        """
        self._sweep_start_max_index = new-1
        self._sweep_stop_max_index = new

    def _sweep_start_value_changed(self, new):
        """
        """
        self._sweep_start_value = new - self.sweep_step_value / 2

    def _sweep_stop_value_changed(self, new):
        """
        """
        self._sweep_stop_value = new - self.sweep_step_value / 2


if __name__ == "__main__":
    SweepBuilder1D(None, None).configure_traits()