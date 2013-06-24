from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api import\
    HasTraits, Int, Str, List, Bool, Any, Instance, Event, Float

from traitsui.api import\
    View, Item, HGroup, Label

from threading import Thread

import numpy

import time

class AbstractDynamicFileReader(HasTraits):
    pass

class DynamicFileReader(AbstractDynamicFileReader):
    """
    """

    updating_time = Float(5.0)
    data_update = Event()

    skip_rows = Int(0)
    comments = ('#')
    delimiter = Str('\t')
    all_columns = Bool(True)
    columns = List(Int)

    _abort = Bool(False)
    _thread = Instance(Thread)
    _file_opened = Any()

    traits_view = View(
                    HGroup(
                        Item('updating_time',
                            label = 'Updating time',
                            width = -30,
                            ),
                        Label('s'),
                        )
                    )

    def __init__(self, static_reader = None, **kwarg):
        super(DynamicFileReader, self).__init__(**kwarg)
        #convenience assuming that the dynamic reader is linked against a
        #static one
        if static_reader is not None:
            self.sync_trait('delimiter', static_reader)
            self.sync_trait('skip_rows', static_reader)
            self.sync_trait('comments', static_reader)
            self.sync_trait('all_columns', static_reader)
            self.sync_trait('columns', static_reader)

    def read_data(self, filename, lines_loaded, dtype = None):
        self._thread = Thread(None, self._read_data, args = (filename,
                                                             lines_loaded,
                                                             dtype))
        self._thread.start()

    def abort_reading(self):
        self._abort = True
        self._thread.join()
        self._abort = False

    def _read_data(self, filename, lines_loaded, dtype):
        self._file_opened = open(filename)
        i = 0
        #skip the lines read already if any
        while i < lines_loaded + 1 + self.skip_rows:
            if not self._file_opened.readline().startswith(self.comments) :
                i += 1
            where = self._file_opened.tell()

        #actual reading
        line_list = []
        while not self._abort:
            line = self._file_opened.readline()
            #Process the line if there is one
            if line:
                new = tuple([eval(x) for x in line.split(self.delimiter)])
                if not self.all_columns:
                    new = [new[x-1] for x in self.columns]
                line_list.append(new)
            #Fire the event if no line remain to be read
            else:
                if line_list:
                    if dtype is not None:
                        self.data_update = numpy.array(line_list,
                                                           dtype = dtype)
                    else:
                        self.data_update = line_list

                if not self._abort:
                    where = self._file_opened.tell()
                    time.sleep(self.updating_time)
                    self._file_opened.seek(where)
                    #empty the list
                    line_list = []



if __name__ == "__main__":
    DynamicFileReader().configure_traits()
