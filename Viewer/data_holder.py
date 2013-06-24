"""
"""
from traits.api\
    import HasTraits, Event, Dict, Array, Str

from threading\
    import RLock

from numpy\
     import array, concatenate

class DataHolder(HasTraits):
    """
    """

    #Public properties
    data_update = Event(Dict)

    #Private properties
    _datas = Dict(Str, Array, {'main' : array([[0,0,0],[1,1,1]])})
    _datas_update = Dict(Str, Array)
    _lock = RLock()

    def __init__(self):
        super(DataHolder, self).__init__()

    #Public methods
    def set_data(self, data_dict, container = None, notify = True):
        """
        """
        self._lock.acquire()
        aux_replaced = []
        aux_new = []
        names = data_dict.keys()
        if container is not None:
            if container in self._datas.keys():
                for name in names:
                    if name in self._datas[container].dtype.names:
                        self._datas[container][name] = data_dict[name]
                        aux_replaced.append(container + ':' + name)
                    else:
                        print 'No field ' + name + ' in the container ' +\
                                container
            else:
                print 'No container ' + container + ' in this data_holder'
        else:
            keys = self._datas.keys()
            for name in names:
                self._datas[name] = data_dict[name]
                if name in keys:
                    aux_replaced.append(name)
                else:
                    aux_new.append(name)

        self._lock.release()
        if notify:
            self.data_update = {'replaced' : aux_replaced, 'new' : aux_new}


    def update_data(self, update_dict, notify = True):
        """
        """
        self._lock.acquire()
        aux_update = []
        update_names = update_dict.keys()
        names = self._datas.keys()

        for name in update_names:
            if name in names:
                new = update_dict[name]
                self._datas_update[name] = new
                old_data = self._datas[name]
                if new.dtype == old_data.dtype:
                    self._datas[name] = concatenate((old_data, new))
                    aux_update.append(name)
                else:
                    if type(new) is list and type(new[0]) is tuple:
                        self._datas[name] = concatenate(old_data, new)
                        aux_update.append(name)
                    else:
                        print 'Unformatted data should be passed as list of\
                            tuple'
            else:
                print 'No field ' + name + 'in the datas'

        self._lock.release()
        if notify:
            self.data_update = {'update' : aux_update}

    def get_data(self, name, container = None):
        """
        """
        if name is not None:
            self._lock.acquire()
            success = False
            entries = self._datas.keys()
            if container is not None:
                if container in entries:
                    if name in self._datas[container].dtype.names:
                        data = self._datas[container][name]
                        success = True
                    else:
                        print 'No field ' + name + ' in container ' + container
                        return None
                else:
                    print 'No container ' + container + ' in the data'
                    return None
            else:
                if name in entries:
                    data = self._datas[name]
                    success = True
                else:
                    for entry in entries:
                        names = self._datas[entry].dtype.names
                        if names is not None:
                            if name in self._datas[entry].dtype.names:
                                data = self._datas[entry][name]
                                success = True
                                break

            self._lock.release()
            if success:
                return data
            else:
                print 'No field ' + name + 'in the data'
                return None

    def get_update(self, name, container = None):
        """
        """
        if name is not None:
            self._lock.acquire()
            success = False
            entries = self._datas_update.keys()
            if container is not None:
                if container in entries:
                    if name in self._datas_update[container].dtype.names:
                        update = self._datas_update[container][name]
                        success = True
                    else:
                        print 'No update for ' + name + ' in container ' +\
                            container
                        return None
                else:
                    print 'No container ' + container + ' in the update'
                    return None
            else:
                if name in entries:
                    update = self._datas_update[name]
                    success = True
                else:
                    for entry in entries:
                        names = self._datas_update[entry].dtype.names
                        if names is not None:
                            if name in self._datas_update[entry].dtype.names:
                                update = self._datas_update[entry][name]
                                success = True
                                break

            self._lock.release()
            if success:
                return update
            else:
                print 'No update available for field ' + name
                return None

    def del_data(self, names, notify = True):
        """
        """
        self._lock.acquire()
        entries = self._datas.keys()
        aux_deleted = []
        for name in names:
            if name in entries:
                del self._datas[name]
                aux_deleted.append(name)
            else:
                print 'No array ' + name + ' to be deleted'

        self._lock.release()
        if notify:
            self.data_update = {'deleted' : aux_deleted}

    def reset_data(self, notify = False):
        """
        """
        self._lock.acquire()
        self._datas = {'main' : array([[0,0,0], [1,1,1]])}
        self._lock.release()
        if notify:
            self.data_update = {'reset' : []}

    def get_keys(self, container):
        """
        """
        self._lock.acquire()
        entries = self._datas.keys()
        self._lock.release()
        if container in entries:
            names = list(self._datas[container].dtype.names)
            if names is None:
                print 'Field ' + container + 'is not a container'
            return names
        else:
            print 'No field ' + container + ' in the data'
            return None

    def is_container(self, container):
        """
        """
        self._lock.acquire()
        entries = self._datas_update.keys()
        self._lock.release()
        if container in entries:
            return self._datas[container].dtype.names is not None
        else:
            print 'No field ' + container + ' in the data'
            return None

if __name__ == "__main__":
    a = DataHolder()
    a.get_data(None)
