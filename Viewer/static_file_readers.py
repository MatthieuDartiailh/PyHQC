from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api import\
    Int, Str, List, Bool, Event

from traitsui.api import\
    View, Item, VGroup, CSVListEditor

from pandas.io.parsers import read_csv

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
                frame = read_csv(filename, comment = self.comments,
                                 delimiter = None, usecols = aux,
                                 skiprows = self.skip_rows + comment_lines)
                return frame.to_records(index=False)
            else:
                frame = read_csv(filename, comment = self.comments,
                                 delimiter = self.delimiter,
                                 skiprows = self.skip_rows + comment_lines)
                return frame.to_records(index=False)

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
            frame = read_csv(filename, comment = self.comments,
                             delimiter = None, usecols = aux,
                             skiprows = self.skip_rows + comment_lines)
            self.data = frame.to_records(index=False)
        else:
            frame = read_csv(filename, comment = self.comments,
                             delimiter = self.delimiter,
                             skiprows = self.skip_rows + comment_lines)
            self.data = frame.to_records(index=False)

if __name__ == "__main__":
    StaticFileReader().configure_traits()
