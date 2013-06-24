"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, List, Str, Instance,\
            Bool, Button, on_trait_change

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Spring,\
        ListStrEditor, Group

from threading import Thread

from plotter_1d import Plotter1D

from data_holder import DataHolder

from sweep_builder_1d import SweepBuilder1D

from function_applier_1d import FunctionApplier1D

class DataParser1D(HasTraits):
    """
    """
    #Properties
    columns = List(Str)
    x_column = Str
    y_columns = List(Str)
    auto_update = Bool()
    update = Button(label = 'Update')
    sweep_builder = Instance(SweepBuilder1D)
    function_1d = Instance(FunctionApplier1D)

    #Private properties
    _plotter = Instance(Plotter1D)
    _data_holder = Instance(DataHolder)


    view = View(
                VGroup(
                    HGroup(
                        Spring(),
                        UItem('update', style = 'custom',
                              enabled_when = 'not auto_update'),
                        Item('auto_update'),
                        Spring(),
                        ),
                    VGroup(
                        Group(
                            UItem('columns',
                                 editor = ListStrEditor(
                                                selected = 'x_column',
                                                editable = False,),
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
        self._plotter = plotter
        self._data_holder = data_holder
        self.sweep_builder = SweepBuilder1D(data_holder, self)
        self.function_1d = FunctionApplier1D()
        self.auto_update = True

        self.on_trait_change(self.on_data_update, '_data_holder:data_update',
                             dispatch = 'ui')

    @on_trait_change('auto_update')
    def switch_auto_update(self, new):
        """
        """
        if new :
            rem = False
            self.update_plot()
        else:
            rem = True

        self.on_trait_change(self.new_selected_x,
                             'x_column', remove = rem)
        self.on_trait_change(self.new_selected_y,
                             'y_columns', remove = rem)
        self.on_trait_change(self.update_plot,
                             'sweep_builder:request_replot', remove = rem)
        self.on_trait_change(self.update_plot,
                             'function_1d:request_replot', remove = rem)

    @on_trait_change('update')
    def update_plot(self):
        """
        """
        #When setting the data of the array plot data, only one array can be
        #set at a time so cannot optimize
        x_thread = Thread(target = self._new_x_plot_data)
        x_thread.start()
        y_thread = Thread(target = self._new_y_plot_data)
        y_thread.start()

    #convenience function to make 1d parser and 2d parser similars
    def new_selected_x(self):
        """
        """
        x_thread = Thread(target = self._new_x_plot_data)
        x_thread.start()

    #convenience function to make 1d parser and 2d parser similars
    def new_selected_y(self):
        """
        """
        y_thread = Thread(target = self._new_y_plot_data)
        y_thread.start()

    #@on_trait_change('_data_holder:data_update', dispatch = 'ui')
    #Here we must update the GUI through traits so we dispatch to 'ui'
    def on_data_update(self, new):
        """
        """
#        print 'data_parser_1d data_update printing new : {}'.format(new)
        for key in new.keys():
            if key == 'update':
                fields = []
                for field in new[key]:
#                    print 'data_parser_1d data_update printing field : {}'.format(field)
                    if self._data_holder.is_container(field):
                        fields += self._data_holder.get_keys(field)
                    else:
                        fields.append(field)
#                print 'data_parser_1d data_update printing fields : {}'.format(fields)
                xy = [self.x_column]+self.y_columns
#                print 'data_parser_1d data_update printing xy : {}'.format(xy)
                if len([field for field in fields if field in xy]) == len(xy)\
                                                    and self.auto_update:
                    up_thread = Thread(target = self._process_update)
                    up_thread.start()

            if key == 'replaced':
                if 'main' in new[key]:
                    # everything changed as the loader first empty the
                    #data_holder
                    keys = self._data_holder.get_keys('main')
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

                    if self.auto_update:
                        self.update_plot()
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

    def _new_x_plot_data(self):
        """
        """
        if self.x_column is not '':
            if self._plotter.x_axis_label != self.x_column:
                self._plotter.x_axis_label = self.x_column

            new_x = self._data_holder.get_data(self.x_column)
            new_x, copy = self.sweep_builder.filter_data([new_x])

            #Set the data (don't worry about thread here)
            self._plotter.data.set_data('x', new_x[0])

    def _new_y_plot_data(self):
        """
        """
        if self.y_columns: #test for empty list
            if self._plotter.y_axis_label != self.y_columns[0]:
                self._plotter.y_axis_label = self.y_columns[0]

            #Process the data for each selected y
            made_copy = False
            #First we get the datas
            new_y_list = [self._data_holder.get_data(name)\
                            for name in self.y_columns]

            #We build the sweeps
            new_y_list, copy = self.sweep_builder.filter_data(new_y_list)
            #Remember if we work on a copy or not
            made_copy = made_copy or copy
            if not made_copy and self.function_1d.active:
                new_ys = [new_y.copy() for new_y in new_y_list]
            else:
                new_ys = new_y_list

            #Apply the function (does nothing in the inactivate case)
            new_ys = self.function_1d.process(new_ys)

            #Set the data (don't worry about thread here)
            for i, new_y in enumerate(new_ys):
                self._plotter.data.set_data('y{}'.format(i), new_y)

            #remove unnecessary entries in the plot data
            for i in range(len(self.y_columns), \
                                 len(self._plotter.plot.plots.keys())):
                self._plotter.data.del_data('y{}'.format(i))

    def _process_update(self):
        """
        """
#        print 'data_parser 1d process update entry'
        #Get all the data
        x_update = [self._data_holder.get_update(self.x_column)]
        y_updates = [self._data_holder.get_update(y_col)\
                        for y_col in self.y_columns]
        x_plot_data = [self._plotter.data.get_data('x')]
        y_plot_datas = [self._plotter.data.get_data('y{}'.format(i))\
                        for i in xrange(len(y_updates))]
        x_data = [self._data_holder.get_data(self.x_column)]
        y_datas = [self._data_holder.get_data(y_col)\
                        for y_col in self.y_columns]

        #Apply function to the updates
        updates = self.function_1d.update(x_update + y_updates)

        #Update plot data (we need data for exotic case in which we must
        #rebuild the whole sweeps)
        plot_data_list, raw_data = self.sweep_builder.update_data(updates,
                                                   x_plot_data + y_plot_datas,
                                                   x_data + y_datas)
        x_plot_data = plot_data_list[0]
        y_plot_datas = plot_data_list[1::]
        #Apply function
        if raw_data:
            y_plot_datas = self.function_1d.process(y_plot_datas)
        else:
            y_plot_datas = self.function_1d.update(y_plot_datas)

        #Set the data (don't worry about thread here)
        self._plotter.data.set_data ('x', x_plot_data)
        for i, y_plot_data in enumerate(y_plot_datas):
            self._plotter.data.set_data('y{}'.format(i), y_plot_data)

if __name__ == "__main__":
    DataParser1D(None, None).configure_traits()
