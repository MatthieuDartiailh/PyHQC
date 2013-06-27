"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import File, Directory, List, Str, on_trait_change

from traitsui.api\
    import View, UItem, VGroup, EnumEditor, TextEditor

import os

from has_preference_traits import HasPreferenceTraits

#TO DO: add folder watch
class DirectoryAndFileChooser(HasPreferenceTraits):
    """
    """

    directory = Directory(preference = 'sync')
    file_list = List(Str)
    file_name = Str(preference = 'sync')
    file = File()

    traits_view = View(
                VGroup(
                    VGroup(
                        UItem('directory'),
                        label = 'Select a directory',
                        show_border = True),
                    VGroup(
                        UItem('file_name',
                                editor = EnumEditor(name = 'file_list')),
                        label = 'Select a file',
                        show_border = True),
                    VGroup(
                        UItem('file', style = 'custom', height = -40,
                              editor = TextEditor(multi_line = True,
                                                  read_only = True)),
                        label = 'File',
                        show_border = True),
                    ),
                resizable = True)

    def __init__(self, pref_name = None, pref_parent = None, **kwargs):
        super(DirectoryAndFileChooser, self).__init__(pref_name, pref_parent,
                                                        **kwargs)
        self.preference_init()

    @on_trait_change('directory')
    def update_directory(self,new):
        """
        """
        self.directory = os.path.normpath(new)

    @on_trait_change('directory')
    def update_list_file(self):
        """
        """
        self.file_list = os.listdir(self.directory)

    @on_trait_change('file_name')
    def build_file(self):
        """
        """
        self.file = os.path.join(self.directory,self.file_name)

if __name__ == "__main__":
    DirectoryAndFileChooser().configure_traits()