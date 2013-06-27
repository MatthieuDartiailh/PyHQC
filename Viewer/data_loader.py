"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Str, Instance, Array, Bool, Button, Long, File,\
        on_trait_change

from traitsui.api\
    import View, UItem, VGroup, HGroup, Item, Controller, Spring, InstanceEditor

from traitsui.ui_editors.array_view_editor\
    import ArrayViewEditor

from pyface.api\
    import ImageResource

from time\
    import sleep

from has_preference_traits import HasPreferenceTraits
from directory_and_file_chooser import DirectoryAndFileChooser
from static_file_readers import StaticFileReader
from dynamic_file_readers import DynamicFileReader
from data_holder import DataHolder

class ArrayView(HasTraits):
    """
    """

    array = Array

    def __init__(self, data):
        super(ArrayView, self).__init__()
        if data.dtype.names is not None:
            self.array = data.view((float,len(data.dtype.names)))
            data_view = View(
                UItem('array',
                        editor = ArrayViewEditor(
                                    titles = list(data.dtype.names),
                                    format = '%.4e',
                                    show_index = False,
                                    )
                    ),
                resizable = True,
                width = 800,
                height = 500)
            self.trait_view('data_view',data_view)
        else:
            self.array = data
            data_view = View(
                UItem('array',
                        editor = ArrayViewEditor(
                                    format = '%.4e',
                                    show_index = False,
                                    )
                    ),
                resizable = True,
                width = 800,
                height = 500)
            self.trait_view('data_view',data_view)


class DataLoaderController(Controller):
    """
    """
    def object_show_data_changed(self, info):

        model = info.object
        data = model.data_holder.get_data('main')
        aux = ArrayView(data)
        aux.edit_traits(parent = info.ui.control)

class DataLoader(HasPreferenceTraits):
    """
    """

    file_chooser = Instance(DirectoryAndFileChooser)
    filename = File()
    file_reader_static = Instance(StaticFileReader)
    edit_static = Bool(False)
    file_reader_dynamic = Instance(DynamicFileReader)
    edit_dynamic = Bool(False)
    data_holder = Instance(DataHolder)
    data_viewable = Array
    status = Str('')
    lines_loaded = Long
    enable_dynamic = Bool(False)
    show_data = Button(label = 'Show data')
    load_button = Button(style = 'toolbar', label = 'Load',
                           image = ImageResource('Play-Normal-icon.png',
                                            search_path = ['Icon'])
                            )

    #Private properties
    _allow_dynamic_start = Bool(False)

    traits_view = View(
                    VGroup(
                        UItem('file_chooser', style = 'custom'),
                        HGroup(
                            Spring(),
                            Item('enable_dynamic',label = 'Dynamic\n loading'),
                            UItem('load_button'),
                            Spring(),
                            ),
                        HGroup(
                            Spring(),
                            Item('status', label = 'Status',
                                style = 'readonly'
                                ),
                            Spring(),
                            ),
                        HGroup(
                            Spring(),
                            Item('lines_loaded', label = 'Lines loaded',
                             style = 'readonly'),
                            Spring(),
                            ),
                        HGroup(
                            Spring(),
                            UItem('file_reader_static',
                                 defined_when = ('edit_static')
                                 ),
                            UItem('file_reader_dynamic',
                                 defined_when = ('edit_dynamic')
                                 ),
                            Spring(),
                            label = 'Settings',
                            show_border = True
                            ),
                        HGroup(
                            Spring(),
                            UItem('show_data'),
                            Spring(),
                            ),
                        Spring(),
                        ),
                    resizable = True,
                    handler = DataLoaderController()
                    )

    preference_view = View(
                        HGroup(
                            VGroup(
                                UItem('file_reader_static',
                                      editor = InstanceEditor(
                                          view = 'preferece_view'),
                                      ),
                                 show_border = True,
                                 label = 'General parameters',
                                 ),
                            VGroup(
                                UItem('file_reader_dynamic',
                                      editor = InstanceEditor(
                                          view = 'preferece_view'),
                                      ),
                                 show_border = True,
                                 label = 'Dynamic',
                                 ),
                                )
                            )

    def __init__(self, data_holder, edit_static = True, edit_dynamic = True,
                 **kwarg):

        super(DataLoader, self).__init__(**kwarg)
        self.file_chooser = DirectoryAndFileChooser(pref_name = '''Directory
                                                    and file chooser''',
                                                    pref_parent = self)
        self.data_holder = data_holder
        self.edit_static = edit_static
        self.edit_dynamic = edit_dynamic
        self.file_reader_static = StaticFileReader(_use_thread = True,
                                                   pref_name = '''Static file
                                                   reader''',
                                                   pref_parent = self)
        self.file_reader_dynamic = DynamicFileReader(self.file_reader_static,
                                                     pref_name = '''Dynamic file
                                                     reader''',
                                                     pref_parent = self)
        self.preference_init()

    @on_trait_change('file_chooser:file')
    def new_file_selected(self, new):
        """
        """
        self._allow_dynamic_start = False
        self.filename = new

    @on_trait_change('load_button')
    def start_data_loading(self):
        """
        """

        self.lines_loaded = 0
        if self.status == 'UPDATING':
            self.file_reader_dynamic.abort_reading()

        self.status = 'LOADING'
        self.file_reader_static.read_data(filename = self.file_chooser.file)
        #the dynamic part is started _static_data_loaded called when the data
        #event of the static file reader is fired

    @on_trait_change('enable_dynamic')
    def switch_dynamic(self, new):
        """
        """
        if new:
            if self._allow_dynamic_start:
                if self.status == 'LOADING' or self.status == 'LOADED':
                    while self.status == 'LOADING':
                        sleep(0.2)
                    self.status = 'UPDATING'
                    dtype = self.data_holder.get_data('main').dtype
                    self.file_reader_dynamic.read_data(self.filename,
                                                        self.lines_loaded,
                                                        dtype)
        if not new:
            if self.status == 'UPDATING':
                self.file_reader_dynamic.abort_reading()
                self.status = 'LOADED'

    @on_trait_change('file_reader_static:data')
    def _static_data_loaded(self, new):
        """
        """
        self.data_holder.reset_data(notify = False)
        self.data_holder.set_data({'main': new})
        self.lines_loaded = new.shape[0]
        self._allow_dynamic_start = True

        if self.enable_dynamic:
            self.status = 'UPDATING'
            self.file_reader_dynamic.read_data(self.file_chooser.file,
                                                self.lines_loaded,
                                                new.dtype)
        else:
            self.status = 'LOADED'

    @on_trait_change('file_reader_dynamic:data_update')
    def _dynamic_data_loaded(self, new):
        """
        """
        self.lines_loaded += new.shape[0]
        self.data_holder.update_data({'main' : new})

if __name__ == "__main__":
    DataLoader().configure_traits()