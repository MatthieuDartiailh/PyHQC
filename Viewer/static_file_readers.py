from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api import\
    Int, Str, List, Bool, Event

from traitsui.api import\
    View, Item, VGroup, CSVListEditor, HTMLEditor

import numpy

from threading import Thread

from has_preference_traits import HasPreferenceTraits

class AbstractStaticFileReader(HasPreferenceTraits):
    pass

class StaticFileReader(AbstractStaticFileReader):
    """
    """

    #Public properties
    skip_rows = Int(0, preference = 'async')
    comments = Str('#', preference = 'async')
    delimiter = Str('\t', preference = 'async')
    all_columns = Bool(True, preference = 'async')
    columns = List(Int, preference = 'async')
    data = Event()

    #Private poreperties
    _use_thread = Bool(True)

    traits_view = View(
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
        self.preference_init()

    def read_data(self, filename = None):
        """
        """
        if self._use_thread:
            self.thread = Thread(None, self._read_data,args = (filename,))
            self.thread.start()
        else:
            comment_lines = 0
            with open(filename) as f:
                while True:
                    if f.readline().startswith(self.comments):
                        comment_lines += 1
                    else:
                        break
            
            if not self.all_columns :
                aux = tuple([ i-1 for i in self.columns])
                return numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = None, names = True, usecols = aux,
                            skip_header = self.skip_rows + comment_lines)
            else:
                return numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = self.delimiter, names = True,
                            skip_header = self.skip_rows + comment_lines)


    def _read_data(self, filename = None):
        comment_lines = 0
        with open(filename) as f:
            while True:
                if f.readline().startswith(self.comments):
                    comment_lines += 1
                else:
                    break
                
        if not self.all_columns :
            aux = tuple([ i-1 for i in self.columns])
            self.data = numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = None, names = True, usecols = aux,
                            skip_header = self.skip_rows + comment_lines)
        else:
            self.data = numpy.genfromtxt(filename, comments = self.comments,
                            delimiter = self.delimiter, names = True,
                            skip_header = self.skip_rows + comment_lines)

if __name__ == "__main__":
    StaticFileReader().configure_traits()
