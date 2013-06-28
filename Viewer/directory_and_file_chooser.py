"""
"""
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import File, Directory, List, Str, on_trait_change, Instance

from traitsui.api\
    import View, UItem, VGroup, EnumEditor, TextEditor

import os

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch
from watchdog.events import FileSystemEventHandler, FileCreatedEvent,\
                            FileDeletedEvent, FileMovedEvent

from has_preference_traits import HasPreferenceTraits

class FileListUpdater(FileSystemEventHandler):
    """
    """
    def __init__(self, file_chooser):
        self.file_chooser = file_chooser

    def on_created(self, event):
        super(FileListUpdater, self).on_created(event)
        if isinstance(event, FileCreatedEvent):
            self.file_chooser.update_list_file()

    def on_deleted(self, event):
        super(FileListUpdater, self).on_deleted(event)
        if isinstance(event, FileDeletedEvent):
            self.file_chooser.update_list_file()

    def on_moved(self, event):
        super(FileListUpdater, self).on_deleted(event)
        if isinstance(event, FileMovedEvent):
            self.file_chooser.update_list_file()


class DirectoryAndFileChooser(HasPreferenceTraits):
    """
    """

    directory = Directory(preference = 'sync')
    file_list = List(Str)
    file_name = Str(preference = 'sync')
    file = File()
    observer = Instance(Observer,())
    event_handler = Instance(FileListUpdater)
    watch = Instance(ObservedWatch)

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

    def __init__(self, **kwargs):
        super(DirectoryAndFileChooser, self).__init__(**kwargs)
        self.event_handler = FileListUpdater(self)
        self.preference_init()

    @on_trait_change('directory')
    def update_directory(self,new):
        """
        """
        self.directory = os.path.normpath(new)
        if self.watch:
            self.observer.unschedule(self.watch)

        self.watch = self.observer.schedule(self.event_handler, self.directory)
        if not self.observer.isAlive():
            self.observer.start()

    @on_trait_change('directory')
    def update_list_file(self):
        """
        """
        # sorted files only
        path = self.directory
        files = sorted(f for f in os.listdir(path)
                           if os.path.isfile(os.path.join(path, f)))
        self.file_list = files

    @on_trait_change('file_name')
    def build_file(self):
        """
        """
        self.file = os.path.join(self.directory,self.file_name)

if __name__ == "__main__":
    DirectoryAndFileChooser().configure_traits()