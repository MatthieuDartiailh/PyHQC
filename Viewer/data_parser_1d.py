"""
"""
#TODO implement the queue update (not urgent)
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, List, Str, Instance,\
            Bool, Button, on_trait_change

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Spring, EnumEditor,\
        ListStrEditor, Group

from Queue import Queue

from plotter_1d import Plotter1D
from data_holder import DataHolder
from data_filter import DataFilterList
from sweep_builder_1d import SweepBuilder1D
from function_applier_1d import FunctionApplier1D
from consumer_thread import ConsumerThread

class DataParser1D(HasTraits):
    """
    """
    #Attributes
    plotter = Instance(Plotter1D)
    data_holder = Instance(DataHolder)
    sweep_builder = Instance(SweepBuilder1D)
    filter_1d = Instance(DataFilterList)
    function_1d = Instance(FunctionApplier1D)

    columns = List(Str)
    x_column = Str
    y_columns = List(Str)

    auto_update = Bool()
    update = Button(label = 'Update')

    _working_thread = Instance(ConsumerThread)
    _work_queue = Instance(Queue)

    view = View(
                VGroup(
                    HGroup(
                        Spring(),
                        UItem('update', style = 'custom',
                              enabled_when = 'not auto_update'),
                        Item('auto_update'),
                        Spring(),
                        ),
                    HGroup(
                        UItem('filter_1d', style = 'custom'),
                        show_border = True,
                        label = 'Filter',
                           ),
                    VGroup(
                       HGroup(
                            UItem('x_column',
                                 editor = EnumEditor(name = 'columns'),
                                 springy = True
                                 ),
                            label = 'X axis',
                            ),
                        Group(
                            UItem('columns',
                                  editor = ListStrEditor(
                                                selected = 'y_columns',
                                                editable = False,
                                                multi_select = True,
                                                ),
                                ),
                            label = 'Y axis',
                            ),
                        label = 'Axis',
                        show_border = True,
                        ),
                    VGroup(
                        UItem('function_1d', style = 'custom'),
                        show_border = True,
                        label = 'Functions',
                        ),
                    VGroup(
                        UItem('sweep_builder', style = 'custom'),
                        show_border = True,
                        label = 'Sweep',
                        ),
                    ),
                width = -300,
                )


    def __init__(self, plotter, data_holder):

        super(DataParser1D, self).__init__()
        self.plotter = plotter
        self.data_holder = data_holder
        self.filter_1d = DataFilterList(data_holder = data_holder)
        self.sweep_builder = SweepBuilder1D(data_holder, self.filter_1d)
        self.function_1d = FunctionApplier1D()

        self.sync_trait('columns', self.filter_1d)
        self.sync_trait('columns', self.sweep_builder)


        self.on_trait_change(self.on_data_update, 'data_holder:data_update',
                             dispatch = 'ui')
        self.auto_update = True

        self._work_queue = Queue()
        self._working_thread = ConsumerThread(self._work_queue)

    @on_trait_change('update')
    def update_plot(self, name, new):
        """
        """
        if self.x_column and self.y_columns:
            if self._working_thread.isAlive():
                self._working_thread.interrupt = True
                self._working_thread.join()
                self._work_queue = Queue()

            self._work_queue.put({'target' : self._update_plot})
            self._working_thread = ConsumerThread(self._work_queue)
            self._working_thread.start()

    @on_trait_change('auto_update')
    def switch_auto_update(self, new):
        """
        """
        if new :
            rem = False
            self.update_plot('update', None)
        else:
            rem = True

        self.on_trait_change(self.new_selected_x,
                             'x_column', remove = rem)
        self.on_trait_change(self.new_selected_y,
                             'y_columns', remove = rem)
        self.on_trait_change(self.update_plot,
                             'sweep_builder:request_replot', remove = rem)
        self.on_trait_change(self.update_plot,
                             'filter_1d:request_replot', remove = rem)
        self.on_trait_change(self.update_plot,
                             'function_1d:request_replot', remove = rem)

    #@on_trait_change('data_holder:data_update', dispatch = 'ui')
    #Here we must update the GUI through traits so we dispatch to 'ui'
    def on_data_update(self, new):
        """
        """
        for key in new.keys():
            if key == 'update':
                fields = []
                for field in new[key]:
                    if self.data_holder.is_container(field):
                        fields += self.data_holder.get_keys(field)
                    else:
                        fields.append(field)

                xy = [self.x_column] + self.y_columns

                #If the filters are active and functionnal we need an update of
                #it too
                xy += self.filter_1d.active_filters()

                # If the sweep builder is active need an update of its values too
                xy += [self.sweep_builder.sweep_column]

                if len([field for field in fields if field in xy]) == len(xy)\
                                                    and self.auto_update:


                    sweep_update = self.data_holder.get_update(
                                            self.sweep_builder.sweep_column)
                    x_update = self.data_holder.get_update(self.x_column)
                    y_updates = [self.data_holder.get_update(y_column) for
                                    y_column in self.y_columns]
                    self.sweep_builder.refresh_sweep_data()
                    if len(xy) > 3:
                        self.filter_1d.update_filter_values()

                    self._work_queue.put(
                                    {'target' : self._process_update,
                                    'kwargs' : {'sweep_update' : sweep_update,
                                                'x_update' : x_update,
                                                'y_updates' : y_updates
                                                }})

                    if not self._working_thread.isAlive():
                        self._working_thread = ConsumerThread(self._work_queue)
                        self._working_thread.start()

#                if len([field for field in fields if field in xy]) == len(xy)\
#                                                    and self.auto_update:
#                    up_thread = Thread(target = self._process_update)
#                    up_thread.start()

            if key == 'replaced':
                if 'main' in new[key]:
                    # everything changed as the loader first empty the
                    #data_holder
                    keys = self.data_holder.get_keys('main')
                    self.columns = keys
                    #if one of the column name changed we go back to default
                    if self.x_column not in keys or\
                        any([y_col not in keys for y_col in self.y_columns]):

                        if self.auto_update:
                            self.on_trait_change(self.new_selected_x,
                                 'x_column', remove = True)
                            self.on_trait_change(self.new_selected_y,
                                 'y_column', remove = True)

                        self.x_column = keys[0]
                        self.y_columns = [keys[1]]

                        if self.auto_update:
                            self.on_trait_change(self.new_selected_x,
                                 'x_column')
                            self.on_trait_change(self.new_selected_y,
                                 'y_column')

                    if self.sweep_builder.sweep_column not in keys:
                        self.sweep_builder.show_all = True
                        self.sweep_builder.sweep_column = keys[0]
                    else:
                        self.sweep_builder.refresh_sweep_data()

                    if self.auto_update:
                        self.update_plot('', None)
                else:
                    x_rep = self.x_column in new[key]
                    y_rep = any([y_col in new[key]\
                                        for y_col in self.y_columns])

                    if x_rep and self.auto_update:
                        self.new_selected_x()
                    if y_rep and self.auto_update:
                        self.new_selected_y()

            if key == 'new':
                self.columns += new[key]

            if key == 'deleted':
                remove_set = set(new[key])
                self.columns[:] = [column for column in self.columns\
                                            if column not in remove_set]

    def new_selected_x(self):
        """
        """
        if self._working_thread.isAlive():
            self._working_thread.interrupt = True
            self._working_thread.join()
            self._work_queue = Queue()

        self._work_queue.put({'target' : self._new_x_plot_data})
        self._working_thread = ConsumerThread(self._work_queue)
        self._working_thread.start()

    def new_selected_y(self):
        """
        """
        if self._working_thread.isAlive():
            self._working_thread.interrupt = True
            self._working_thread.join()
            self._work_queue = Queue()

        self._work_queue.put({'target' : self._new_y_plot_data})
        self._working_thread = ConsumerThread(self._work_queue)
        self._working_thread.start()

    def _update_plot(self):

        x = self._new_x_plot_data(retur = True)
        self._new_y_plot_data(new_x = x)

    def _new_x_plot_data(self, retur = False):
        """
        """
        if self.plotter.x_axis_label != self.x_column:
            self.plotter.x_axis_label = self.x_column

        new_x = self.data_holder.get_data(self.x_column)
        [new_x], copy = self.filter_1d.filter_data([new_x])
        [new_x], copy = self.sweep_builder.build_sweep([new_x])

        if retur:
            return new_x
        self.plotter.data.set_data('x', new_x)

    def _new_y_plot_data(self, new_x = None):
        """
        """
        if self.plotter.y_axis_label != self.y_columns[0]:
            self.plotter.y_axis_label = self.y_columns[0]

        #Process the data for each selected y
        made_copy = False
        #First we get the datas
        new_y_list = [self.data_holder.get_data(name)\
                        for name in self.y_columns]

        #We build the sweeps
        new_y_list, copy = self.filter_1d.filter_data(new_y_list)
        new_y_list, copy = self.sweep_builder.build_sweep(new_y_list,
                                                          new_x = False)
        #Remember if we work on a copy or not
        made_copy = made_copy or copy
        if not made_copy and self.function_1d.active:
            new_ys = [new_y.copy() for new_y in new_y_list]
        else:
            new_ys = new_y_list

        #Apply the function (does nothing in the inactivate case)
        new_ys = self.function_1d.process(new_ys)

        if new_x is not None:
            self.plotter.data.set_data('x', new_x)

        for i, new_y in enumerate(new_ys):
            self.plotter.data.set_data('y{}'.format(i), new_y)

        #remove unnecessary entries in the plot data
        for i in range(len(self.y_columns), \
                             len(self.plotter.plot.plots.keys())):
            self.plotter.data.del_data('y{}'.format(i))

    def _process_update(self, sweep_update, x_update, y_updates):
        """
        """

        updates, copy = self.filter_1d.filter_update([sweep_update, x_update] +\
                                                                    y_updates)
        if len(updates[0]) > 0:
            x_plot_data = [self.plotter.data.get_data('x')]
            y_plot_datas = [self.plotter.data.get_data('y{}'.format(i))\
                            for i in xrange(len(y_updates))]

            #Apply function to the updates
            sweep_update = updates[0]
            x_update = updates[1]
            y_updates = self.function_1d.update(updates[2::])
            #Update plot data
            plot_data_list, raw_data = \
                self.sweep_builder.update_sweep(sweep_update,
                                                [x_update] + y_updates,
                                                x_plot_data + y_plot_datas)
            x_plot_data = plot_data_list[0]
            y_plot_datas = plot_data_list[1::]
            #Apply function
            if raw_data:
                y_plot_datas = self.function_1d.process(y_plot_datas)
            else:
                y_plot_datas = self.function_1d.update(y_plot_datas)

            #Set the data (don't worry about thread here)
            self.plotter.data.set_data ('x', x_plot_data)
            for i, y_plot_data in enumerate(y_plot_datas):
                self.plotter.data.set_data('y{}'.format(i), y_plot_data)

if __name__ == "__main__":
    DataParser1D(None, None).configure_traits()
