"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, List, Str, Instance, Bool, Button, Event,\
            on_trait_change

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item,\
            Spring, EnumEditor, ListStrEditor, Group,\
            ButtonEditor

from pyface.api\
    import FileDialog, OK

from threading import Thread
from Queue import Queue

import numpy

import os

from axis_bounds import AxisBounds
from data_loader import DataLoader
from data_holder import DataHolder
from plotter_2d import AutoPlotter2D
from data_filter_2d import DataFilter2D
from function_applier_2d import FunctionApplier2D
from map_builder import MapBuilder
from consumer_thread import ConsumerThread

class DataParser2D(HasTraits):
    """
    """

    loader = Instance(DataLoader)
    plotter = Instance(AutoPlotter2D)
    data_holder = Instance(DataHolder)
    mapper = Instance(MapBuilder)
    filter_2d = Instance(DataFilter2D)
    function_2d = Instance(FunctionApplier2D)

    columns = List(Str)
    x_column = Str
    x_bounds = Instance(AxisBounds)
    y_column = Str
    y_bounds = Instance(AxisBounds)
    index_valid = Bool(False)
    c_column = Str

    auto_update = Bool()
    update = Button(label = 'Update')

    save_matrix = Event
    save_matrix_label = Str('Save')
    save_matrix_ask_file = Bool(False)

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
                        UItem('filter_2d', style = 'custom'),
                        show_border = True,
                        label = 'Filter',
                           ),
                    VGroup(
                        Group(
                            UItem('x_column',
                                 editor = EnumEditor(name = 'columns'),
                                 width = 200
                                 ),
                            label = 'X axis',
                            ),
                        Group(
                            UItem('y_column',
                                  editor = EnumEditor(name = 'columns'),
                                 width = 200
                                ),
                            label = 'Y axis',
                            ),
                        Group(
                            UItem('columns',
                                  editor = ListStrEditor(
                                                selected = 'c_column',
                                                editable = False,
                                                ),
                                ),
                            label = 'Color axis',
                            ),
                        label = 'Axis',
                        show_border = True,
                        ),
                    HGroup(
                        UItem('function_2d', style = 'custom'),
                        show_border = True,
                        label = 'Function'
                        ),
                    HGroup(
                        UItem('save_matrix', editor =\
                            ButtonEditor(label_value = 'save_matrix_label'),
                            ),
                        Item('save_matrix_ask_file',
                             label = 'Ask filename',
                            ),
                        show_border = True,
                        label = 'Save matrix'
                        ),
                    ),
                )



    def __init__(self, loader, plotter, data_holder, **kwargs):

        super(DataParser2D, self).__init__(**kwargs)
        self.x_bounds = AxisBounds([0, 1])
        self.y_bounds = AxisBounds([0, 1])
        self.loader  = loader
        self.plotter = plotter
        self.data_holder = data_holder
        self.mapper = MapBuilder()
        self.function_2d = FunctionApplier2D()
        self.filter_2d = DataFilter2D(data_holder = data_holder)

        self.sync_trait('columns', self.filter_2d)

        if plotter is not None:
            self.x_bounds.sync_trait('min', self.plotter, 'x_min')
            self.x_bounds.sync_trait('max', self.plotter, 'x_max')
            self.y_bounds.sync_trait('min', self.plotter, 'y_min')
            self.y_bounds.sync_trait('max', self.plotter, 'y_max')

        self.on_trait_change(self.on_data_update, 'data_holder:data_update',
                             dispatch = 'ui')
        self.auto_update = True

        self._work_queue = Queue()
        self._working_thread = ConsumerThread(self._work_queue)

    @on_trait_change('update')
    def update_plot(self, name, new):
        """
        """
        if self.x_column and self.y_column and self.c_column:
            if name in ['update', 'filter_active', 'filter_value']:
                self.index_valid = False

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
                             'y_column', remove = rem)
        self.on_trait_change(self.new_selected_c,
                             'c_column', remove = rem)
        self.on_trait_change(self.update_plot,
                             'filter_2d:request_replot', remove = rem)
        self.on_trait_change(self.update_plot,
                             'function_2d:request_replot', remove = rem)

    #@on_trait_change('data_holder:data_update', dispatch = 'ui')
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

                xyc = [self.x_column, self.y_column, self.c_column]

                #If the filter is active and functionnal we need an update of
                #it too
                if self.filter_2d.active and\
                        self.filter_2d.filter_column is not None\
                                and self.filter_2d.value is not None:
                    xyc.append(self.filter_2d.filter_column)

                if len([field for field in fields if field in xyc]) == len(xyc)\
                                                    and self.auto_update:

                    x_update = self.data_holder.get_update(self.x_column)
                    y_update = self.data_holder.get_update(self.y_column)
                    c_update = self.data_holder.get_update(self.c_column)
                    filter_update = None
                    if self.filter_2d.filter_column:
                        filter_update = self.data_holder.get_update(
                                                self.filter_2d.filter_column)
                        self.filter_2d.update_filter_values(filter_update)

                    c_data = self.data_holder.get_data(self.c_column)
                    self._work_queue.put(
                                    {'target' : self._process_update,
                                    'kwargs' : {'x_update' : x_update,
                                                'y_update' : y_update,
                                                'c_update' : c_update,
                                                'filter_update' : filter_update,
                                                'c_data' : c_data}})

                    if not self._working_thread.isAlive():
                        self._working_thread = ConsumerThread(self._work_queue)
                        self._working_thread.start()

            if key == 'replaced':
                if 'main' in new[key]:
                    # everything changed as the loader first empty the
                    #data_holder
                    keys = self.data_holder.get_keys('main')
                    self.columns = keys
                    self.filter_2d.filter_column = keys[0]

                    #if one of the column name changed we go back to default
                    if self.x_column not in keys or self.y_column not in keys\
                        or self.c_column not in keys:

                        if self.auto_update:
                            self.on_trait_change(self.new_selected_x,
                                 'x_column', remove = True)
                            self.on_trait_change(self.new_selected_y,
                                 'y_column', remove = True)
                            self.on_trait_change(self.new_selected_c,
                                 'c_column', remove = True)

                        self.x_column = keys[1]
                        self.y_column = keys[0]
                        if len(keys)>2:
                            self.c_column = keys[2]
                        else:
                            self.c_column = keys[1]

                        if self.auto_update:
                            self.on_trait_change(self.new_selected_x,
                                 'x_column')
                            self.on_trait_change(self.new_selected_y,
                                 'y_column')
                            self.on_trait_change(self.new_selected_c,
                                 'c_column')

                    #We always update the plot
                    if self.auto_update:
                        #We need to check again the indexes so we pass
                        #'update'
                        self.update_plot('update', None)



                else:
                    x_rep = self.x_column in new[key]
                    y_rep = self.y_column in new[key]
                    c_rep = self.c_column in new[key]
                    if x_rep:
                        self.new_selected_x(rebuild = not c_rep or\
                                                (not c_rep and not y_rep))
                    if y_rep:
                        self.new_selected_y(rebuild = not c_rep)
                    if c_rep:
                        self.new_selected_c()

            if key == 'new':
                self.columns += new[key]

            if key == 'deleted':
                remove_set = set(new[key])
                self.columns[:] = [column for column in self.columns\
                                            if column not in remove_set]

    def new_selected_x(self):
        """
        """
        self.index_valid = False
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
        self.index_valid = False
        if self._working_thread.isAlive():
            self._working_thread.interrupt = True
            self._working_thread.join()
            self._work_queue = Queue()

        self._work_queue.put({'target' : self._new_y_plot_data})
        self._working_thread = ConsumerThread(self._work_queue)
        self._working_thread.start()

    def new_selected_c(self):
        """
        """
        if self._working_thread.isAlive():
            self._working_thread.interrupt = True
            self._working_thread.join()
            self._work_queue = Queue()

        self._work_queue.put({'target' : self._new_c_plot_data})
        self._working_thread = ConsumerThread(self._work_queue)
        self._working_thread.start()

    def _update_plot(self):

        self._new_x_plot_data(False)
        self._new_y_plot_data(False)
        self._new_c_plot_data()

    def _new_x_plot_data(self, rebuild = True):
        """
        """

        if self.plotter.x_axis_label != self.x_column:
            self.plotter.x_axis_label = self.x_column

        new_x = self.data_holder.get_data(self.x_column)
        if not self.index_valid:
            new_y = self.data_holder.get_data(self.y_column)
            [new_x, new_y], copy = self.filter_2d.filter_data([new_x, new_y])
            self.index_valid = self._validate_indexes(new_x, new_y)
        else:
            [new_x], copy = self.filter_2d.filter_data([new_x])

        self.mapper.set_data_x(new_x)
        if self.index_valid:
            self.x_bounds.set(new_x)
        else:
            self.x_bounds.set(numpy.linspace(0,0.5,2))

        if rebuild:
            self._replace_data_plotter()

    def _new_y_plot_data(self, rebuild = True):
        """
        """
        if self.plotter.y_axis_label != self.y_column:
            self.plotter.y_axis_label = self.y_column

        new_y = self.data_holder.get_data(self.y_column)
        if not self.index_valid:
            new_x = self.data_holder.get_data(self.x_column)
            [new_x, new_y], copy = self.filter_2d.filter_data([new_x, new_y])
            self.index_valid = self._validate_indexes(new_x, new_y)
        else:
            [new_y], copy = self.filter_2d.filter_data([new_y])

        self.mapper.set_data_y(new_y)
        if self.index_valid:
            self.y_bounds.set(new_y)
        else:
            self.y_bounds.set(numpy.linspace(0,0.5,2))

        if rebuild:
            self._replace_data_plotter()

    def _new_c_plot_data(self):
        """
        """
        if self.c_column is not '':
            if self.plotter.c_axis_label != self.c_column:
                self.plotter.c_axis_label = self.c_column

            self._replace_data_plotter()

    def _validate_indexes(self, new_x, new_y):
        """
        """
        #TODO might want to check on a larger portion of the array
        if len(new_x) > 1 and len(new_y) > 1:
            (replicate,) =  numpy.where(new_x + new_y == new_x[0] + new_y[0])
            if len(replicate) > 1:
                return False
            else:
                return True
        else:
            return True

    def _replace_data_plotter(self):
        """
        """
        made_copy = False
        #First we get the data
        new_c = self.data_holder.get_data(self.c_column)
        #We filter it
        [new_c], copy = self.filter_2d.filter_data([new_c])
        #Remember if we work on a copy or not
        made_copy = made_copy or copy
        #Shape it as a matrix
        new_c, copy = self.mapper.build_map(new_c)
        #Remember if we work on a copy or not
        made_copy = made_copy or copy
        if not made_copy and self.function_2d.active:
            new_d = new_c.copy()
        else:
            new_d = new_c

        #Apply the function (does nothing in the inactivate case)
        new_d = self.function_2d.process(new_d)

        #Set the data (the plotter is thread safe so no worry)
        self.plotter.data.set_data('c', new_d)
        self.plotter.update_plots_index()

    def _process_update(self, x_update, y_update, c_update, filter_update,
                        c_data):
        """
        """
        #Get all the other data
        plot_data = self.plotter.data.get_data('c')

        #Filter the update
        [x_update, y_update, c_update], copy = \
                self.filter_2d.filter_update([x_update, y_update, c_update],
                                             filter_update)

        #Does nothing if update is not in the filter
        if x_update is None:
            print 'parser 2d update filter return'
            return

        #Update bounds
        self.x_bounds.append(x_update)
        self.y_bounds.append(y_update)
        self.mapper.update_data_x(x_update)
        self.mapper.update_data_y(y_update)

        #Make the plot_data ready for update
        plot_data = self.function_2d.pre_update(plot_data)

        #Update plot data (we need c_data for exotic case in which we must
        #rebuild the whole map)
        plot_data, raw_data = self.mapper.update_map(c_update, plot_data, c_data)

        #Apply function
        if raw_data:
            plot_data = self.function_2d.process(plot_data)
        else:
            plot_data = self.function_2d.update(plot_data)

        #Explicitely set the new data and index
        print 'parser 2d update settint c'
        self.plotter.data.set_data('c', plot_data)
        self.plotter.update_plots_index()

    @on_trait_change('save_matrix')
    def save_data_to_matrix(self):
        """
        """
        if self.save_matrix_ask_file:
            def_filename = self.loader.file_chooser.file_name + '_' +\
                            self.c_column
            dialog = FileDialog(action='save as',
                        default_directory = self.loader.file_chooser.directory,
                        default_filename = def_filename)

            if dialog.open() != OK:
                return
            aux = dialog.path
            file_path = os.path.normpath(aux)

            saving_thread = Thread(target = self._save_data_to_matrix,
                                args = (file_path,))
        else:
            saving_thread = Thread(target = self._save_data_to_matrix,
                                args = ())
        saving_thread.start()

    def _save_data_to_matrix(self, file_path = None):
        """
        """
        self.save_matrix_label = 'SAVING...'
        header = 'X axis : {}, min = {: g}, max = {: g};\
                    Y axis : {}, min = {: g}, max = {: g}'.format(\
                    self.x_column, self.x_bounds.min, self.x_bounds.max,\
                    self.y_column, self.y_bounds.min, self.y_bounds.max)

        if file_path is None:
            def_filename = self.loader.file_chooser.file_name + '_' +\
                            self.c_column
            file_path = os.path.join(self.loader.file_chooser.directory,
                                         def_filename)

        if file_path is not None or file_path is not '':
            numpy.savetxt(file_path, self.plotter.data.get_data('c'),
                            delimiter = '\t', header = header)
        self.save_matrix_label = 'Save'


if __name__ == "__main__":
    DataParser2D(None, None, None).configure_traits()
