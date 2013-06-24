"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Instance

from traitsui.api\
    import View, UItem, HGroup

from data_loader import DataLoader
from data_parser_1d import DataParser1D
from plotter_1d import AutoPlotter1D
from data_parser_2d import DataParser2D
from plotter_2d import AutoPlotter2D
from data_holder import DataHolder

class Viewer(HasTraits):
    """
    """

    data_loader = Instance(DataLoader)
    data_holder = Instance(DataHolder)
    parser_1d = Instance(DataParser1D)
    plotter_1d = Instance(AutoPlotter1D)
    parser_2d = Instance(DataParser2D)
    plotter_2d = Instance(AutoPlotter2D)

    trait_view = View(
                    HGroup(
                        UItem('data_loader', style = 'custom',
                                width = 250),
                        HGroup(
                            HGroup(
                                UItem('parser_1d', style = 'custom',
                                        width = -250, resizable = False),
                                UItem('plotter_1d', style = 'custom'),
                                selected = True,
                                label = '1D',
                                ),
                            HGroup(
                                UItem('parser_2d', style = 'custom',
                                        width = -250, resizable = False),
                                UItem('plotter_2d', style = 'custom'),
                                label = '2D',
                                ),
                            layout = 'tabbed',
                            ),
                        layout = 'split'),
                    resizable = True,
                    title = 'Python Viewer',
                    )

    def __init__(self):

        super(Viewer, self).__init__()
        self.data_holder = DataHolder()
        self.data_loader = DataLoader(self.data_holder)
        self.plotter_1d = AutoPlotter1D()
        self.parser_1d = DataParser1D(plotter = self.plotter_1d,
                                      data_holder = self.data_holder)
        self.plotter_2d = AutoPlotter2D()
        self.parser_2d = DataParser2D(loader = self.data_loader,
                                       plotter = self.plotter_2d,
                                       data_holder = self.data_holder)


if __name__ == "__main__":
    viewer = Viewer()
    viewer.configure_traits()