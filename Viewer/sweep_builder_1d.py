"""
"""

from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, List, Str, Instance, Int, Float,\
            Bool, Range, on_trait_change, Event, Enum

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Spring, EnumEditor,\
        Group, TextEditor

from data_holder\
    import DataHolder

from numpy\
    import linspace, concatenate, insert


class SweepBuilder1D(HasTraits):
    """
    """

    show_all = Bool(True)
    columns = List(Str)
    sweep_column = Str

    sweep_start_index = Range(low = 1, high = 10000001, value = 1)
    sweep_stop_index = Range(low = 2, high = 10000002, value = 2)

    sweep_start_value = Float(0.5)
    sweep_stop_value = Float(1.0)
    sweep_step_value = Float(1.0)
    sweep_min_value = Float(0.5)

    sweep_size = Int
    sweep_period = Int

    request_replot = Event

    mode = Enum('contiguous', 'periodic', 'sort')

    _data_holder = Instance(DataHolder)
    _allow_update = Bool(True)

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

    def __init__(self, data_holder, parser, **kwarg):

        super(SweepBuilder1D, self).__init__(**kwarg)
        self._data_holder = data_holder
        self.sync_trait('columns', parser)

    def filter_data(self, data_list):
        """
        """
        made_copy = False
        if self.show_all :
            return data_list, made_copy

        if self.mode == 'contiguous':
            start = self.sweep_size*(self.sweep_start_index-1)
            stop  = self.sweep_size*(self.sweep_stop_index-1)
            #This is safe for numpy array no matter the stop value
            return [ data[start:stop] for data in data_list], made_copy
        else:
            made_copy = True
            sweep = self._data_holder.get_data(self.sweep_column)
            start = self.sweep_start_value
            stop = self.sweep_stop_value
            length = (stop - start)/self.sweep_step_value
            values = linspace(start, stop, length)
            masks = [(sweep == value) for value in values]
            return [concatenate([data[mask] for mask in masks])\
                        for data in data_list], made_copy

    def update_data(self, update_list, plot_data_list, data_list):
        """
        """
        raw_data = False
        if self.show_all :
            return [concatenate((plot_data_list[i], update_list[i]))\
                for i in xrange(len(update_list))], raw_data

        if self.mode == 'contiguous' :
            stop = self.sweep_size*(self.sweep_stop_index-1)
            start = self.sweep_size*(self.sweep_start_index-1)
            available_length = stop - start - len(plot_data_list[0])
            if available_length >= 0:
                for i in xrange(len(plot_data_list)):
                    plot_data_list[i] = concatenate((plot_data_list[i],
                    update_list[i][0:available_length]))

                return plot_data_list, raw_data

            else:
                return plot_data_list, raw_data

        elif self.mode == 'periodic' :
            sweep_update = self._data_holder.get_update(self.sweep_column)
            start = self.sweep_start_value
            stop = self.sweep_stop_value
            length = (stop - start)/self.sweep_step_value
            values = linspace(start, stop, length).tolist()
            for i, value in enumerate(sweep_update):
                if value in values:
                    period_index = values.index(value)
                    for j in xrange(len(plot_data_list)):
                        plot_data_list[j] = insert(plot_data_list[j],
                                    (period_index+1)*self.sweep_period + i,
                                    update_list[j][i])

            return plot_data_list, raw_data

        else:
            #Here we will always return a copy, which is equivalent to raw_data
            # is True
            return self.filter_data(data_list)

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

        self.on_trait_change(self._ask_replot,
                            'sweep_size',remove = new)

    def _ask_replot(self, name, new):
        """
        """
        self.request_replot = {'sweep' : name}

    @on_trait_change('sweep_column')
    def _new_sweep_column(self, new):
        """
        """
        dat = self._data_holder.get_data(new)
        ref = dat[0]
        size = 1
        while ref == dat[size] and size < len(dat):
            size += 1

        self.sweep_size = size

        if size > 1:
            self.mode = 'contiguous'
            self.sweep_min_value = ref
            if len(dat) > self.sweep_size:
                self.sweep_step_value = dat[self.sweep_size]-ref
        else:
            set_dat = set(dat)
            self.sweep_min_value = min(set_dat)
            self.sweep_step_value = \
                (max(set_dat)-self.sweep_min_value)/(len(set_dat)-1)
            if len(dat) > len(set_dat):
                if ref == dat[len(set_dat)]:
                    self.mode = 'periodic'
                    self.sweep_period = len(set_dat)
            else:
                self.mode = 'sort'

        print 'sweep_builder new_sweep column mode : {}'.format(self.mode)
        self.sweep_start_value = ref +\
                    (self.sweep_start_index-1)*self.sweep_step_value
        self.sweep_stop_value = ref +\
                    (self.sweep_stop_index-1)*self.sweep_step_value


    @on_trait_change('sweep_start_index')
    def _new_start_index(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            aux = self.sweep_min_value + (new-1)*self.sweep_step_value
            self.sweep_start_value = aux
            if new > self.sweep_stop_index-1:
                self.sweep_stop_index = new + 1
                aux = self.sweep_min_value + (new)*self.sweep_step_value
                self.sweep_stop_value = aux
            self._allow_update = True

    @on_trait_change('sweep_stop_index')
    def _new_stop_index(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            aux = self.sweep_min_value + (new-1)*self.sweep_step_value
            self.sweep_stop_value = aux
            if new < self.sweep_start_index+1:
                self.sweep_start_index = new-1
                aux = self.sweep_min_value + (new-2)*self.sweep_step_value
                self.sweep_start_value = aux
            self._allow_update = True

    @on_trait_change('sweep_start_value')
    def _new_start_value(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            index = int((new - self.sweep_min_value)/self.sweep_step_value)+1
            if index > 0 and index < 10000001:
                self.sweep_start_index = index

                if index > self.sweep_stop_index-1:
                    self.sweep_stop_index = index+1
                    self.sweep_stop_value = self.sweep_min_value +\
                                            (index)*self.sweep_step_value
            elif index < 1:
                self.sweep_start_index = 1
                self.sweep_start_value = self.sweep_min_value
            else:
                self.sweep_start_index = 10000001
                self.sweep_start_value = self.sweep_min_value +\
                                        10000001*self.sweep_step_value
            self._allow_update = True

    @on_trait_change('sweep_stop_value')
    def _new_stop_value(self, new):
        """
        """
        if self._allow_update:
            self._allow_update = False
            index = int((new - self.sweep_min_value)/self.sweep_step_value)+1
            if index > 1 and index < 10000002:
                self.sweep_stop_index = index

                if index < self.sweep_start_index+1:
                    self.sweep_start_index = index-1
                    aux = self.sweep_min_value +\
                            (index-2)*self.sweep_step_value
                    self.sweep_start_value = aux
            elif index < 2:
                self.sweep_stop_index = 2
                self.sweep_stop_value = self.sweep_min_value +\
                                            self.sweep_step_value
            else:
                self.sweep_stop_index = 10000002
                self.sweep_stop_value = self.sweep_min_value +\
                                        10000002*self.sweep_step_value
            self._allow_update = True

if __name__ == "__main__":
    SweepBuilder1D(None, None).configure_traits()