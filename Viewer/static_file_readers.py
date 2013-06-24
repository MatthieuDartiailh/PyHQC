from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api import\
    HasTraits, Int, Str, List, Bool, Event

from traitsui.api import\
    View, Item, VGroup, CSVListEditor

import numpy

from threading import Thread

class AbstractStaticFileReader(HasTraits):
    pass

class StaticFileReader(AbstractStaticFileReader):
    """
    """

    #Public properties
    skip_rows = Int(0)
    comments = ('#')
    delimiter = Str('\t')
    all_columns = Bool(True)
    columns = List(Int)
    data = Event()

    #Private poreperties
    _use_thread = Bool(True)

    trait_view = View(
                    VGroup(
                        Item('delimiter', label = 'Delimiter'),
                        Item('comments', label = 'Comment'),
                        Item('skip_rows', label = 'Rows to skip'),
                        Item('all_columns',label = 'All columns'),
                        Item('columns', label = 'Columns',
                            enabled_when = 'not all_columns',
                            editor=CSVListEditor(ignore_trailing_sep=False),
                            ),
                        )
                    )

    def __init__(self,**kwarg):
        super(StaticFileReader, self).__init__(**kwarg)

    def read_data(self, filename = None):
        """
        """
        if self._use_thread:
            self.thread = Thread(None, self._read_data,args = (filename,))
            self.thread.start()
        else:
            if not self.all_columns :
                aux = tuple([ i-1 for i in self.columns])
                return numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = None, names = True,
                            usecols = aux)
            else:
                return numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = self.delimiter, names = True)


    def _read_data(self, filename = None):
        if not self.all_columns :
            aux = tuple([ i-1 for i in self.columns])
            self.data = numpy.genfromtxt(filename, comments = self.comments,
                        delimiter = None, names = True,
                        usecols = aux)
        else:
            self.data = numpy.genfromtxt(filename, comments = self.comments,
                        delimiter = self.delimiter, names = True)

if __name__ == "__main__":
    StaticFileReader().configure_traits()
