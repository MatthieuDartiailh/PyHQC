#==============================================================================
# module : has_preference_traits.py
# author : Matthieu Dartiailh
# last modified : 28/05/2013
#==============================================================================
"""Implementation of an easy to use preferences system for HasTraits class

This module defines a single class : HasPreferenceTraits. This class inherits
from HasTraits class and use the configobj package to manage preferences.
"""
from traits.api\
    import HasTraits, Instance, List, Str, Int, This, Unicode, Bool
from traitsui.api\
    import Item, Group, View
from configobj\
     import Section, ConfigObj
from threading\
    import RLock

all_pref = lambda x: (x == 'async' or x == 'sync')

class HasPreferenceTraits(HasTraits):
    """
    HasTraits derived object implementing an easy to use preferences system.

    General purpose class implementing an easy to use preferences system built
    on the configobj package. Preferences are saved in an .ini files.
    Preferences are simply defined by setting the metadata 'property' for the
    trait to be saved as a preference. Possible values for this metadata are:
        - 'async' : for traits which should only be saved when the user asks
        for preferences to be saved.
        - 'sync' : for traits whose value should be saved every time it changes

    Parameters
    ----------
    pref_parent : instance(HasPreferenceTraits)
        Parent of the instance
    pref_name : str
        Name of the preference node represented by this class
    default_file : str, optional
        Path of the file in which to save the preferences, should be specified
        only for the root node of the preferences.
    **kwarg : keyworg arg
        Keyword arguments that should be passed to the HasTraits __init__

    Methods
    -------
    preference_init()
        End the itialisation process.
    save_preferences(filename=str)
        Save the whole preference tree either to the specified file or to the
        default_file
    load_preferences(filename)
        Load preferences from the specified file or the default file if no
        filename is specfied. Only 'async' traits are set by this method

    """
    #==========================================================================
    # Public properties
    #==========================================================================
    merge_ui_with_parent = Bool(False)

    #==========================================================================
    # Private properties
    #==========================================================================
    _preferences = Instance(Section)
    _init_complete = Bool(False)
    _parent = This
    _root = This
    _childs = List()
    _name = Str()
    _depth = Int(0)

    #==========================================================================
    # Public method
    #==========================================================================
    def __init__(self, pref_parent=None, pref_name='',
                    default_file = None, **kwargs):

        super(HasPreferenceTraits, self).__init__(**kwargs)
        #Is this the root node for a preference tree
        if pref_parent is not None:
            pref_parent._preferences[pref_name] = {}
            self._pref_lock = pref_parent._pref_lock
            self._preferences = pref_parent._preferences[pref_name]
            self._depth = pref_parent._depth + 1
            self._root = pref_parent._root
            self._parent = pref_parent
            pref_parent._childs.append(self)

        else:
            self._pref_lock = RLock()
            self._root = self
            if default_file is not None:
                self._preferences = ConfigObj(default_file)
            else:
                self._preferences = ConfigObj()

    def preference_init(self):
        """Method ending the initialisation process of an object

        This method sets up the notification process for 'sync' preferences,
        loads preferences value from the default file (if this node is the root
        node) and initialise the preference view if none was specified in the
        subclass. The _init_complete is then set to true.
        This method should be called at the end of the __init__ method of
        classes subclassing this one. Subclasses must override the __init__
        method as otherwise this method is never called.

        Parameters
        ----------
        none

        Returns
        -------
        none

        """
        #Set initial value of all entries in the tree preference
        for name in self.traits(preference = all_pref):
            self._preferences[name] = str(self.get(name).values()[0])

        #Load default preference and connect notification handler for 'sync'
        #preferences.
        if self._depth == 0 and self._preferences.filename is not None:
            #Load default file and merge preferences with the tree we already
            #created to avoid deleting any key that we need but that does not
            #exist in the file.
            aux = ConfigObj(self._preferences.filename)
            self._preferences.merge(aux)
            self._update_traits_from_prefs(all_traits = True)
            self._init_sync_preferences()

        #Initialise the view
        self._init_pref_view()

        self._init_complete = True

    def save_preferences(self, filename = None):
        """Save the preference tree to the specified file or default one

        Save the whole preference tree by calling the method of the root
        instance of HasPreferenceTraits. Preferences are saved to an .ini files
        which is either specified when the method is called or is the default
        file for the root node.

        Parameters
        ----------
        filename : str, optional
            Path of the file to which preferences will be saved. If left to
            None, preferences will be saved to the default file of the root
            node.

        Returns
        -------
        none
        """
        #Check if we are in root node
        if self._depth != 0:
            self._root.save_preferences(filename = filename)
        else:
            self._update_prefs_from_traits()
            if filename is None:
                self._save_preferences()
            else:
                self._save_preferences(filename)
                #restore the preference tree to its value before saving so that
                #'sync' preference saving does override the default preferences
                #with wrong values
                self._preferences.reload()

    def load_preferences(self, filename = None, all_traits = False):
        """Load preferences from specified or default file and update traits

        Load the preferences for the whole tree by calling the method of the
        root nodestored in the specified file or the default file if none is
        specified. By default only 'async' preferences are updated as the value
        for 'sync' preferences are likely to be non pertinent.

        Parameters
        ----------
        filename : str, optional
            Path of the file from which preferences will be loaded. If left to
            None, preferences will be loaded from the default file of the root
            node.
        all_traits : bool, optional
            Boolean value indicating if 'sync' preferences should be updated
            from the value found in the file.

        Returns
        -------
        none
        """
        if self._depth != 0:
            self._root.load_preferences(filename = filename)
        else:
            if filename is None:
                self._update_traits_from_prefs()
            else:
                aux = ConfigObj(filename)
                self._preferences.merge(aux)
                self._update_traits_from_prefs(all_traits)
                self._preferences.reload()

    #==========================================================================
    # Private methods
    #==========================================================================
    def _init_sync_preferences(self):
        """Method called at init by the root node to connect 'sync' preferences

        This method is called at init by the root node to connect the
        notification handlers for the 'sync' preference. This is done after the
        loading of default preferences to avoid a lot of useless notifications.

        Parameters
        ----------
        none

        Returns
        -------
        none
        """
        for name in self.traits(preference = 'sync').keys():
            self.on_trait_change(self._update_and_save, name,
                                                dispatch = 'new')

        for child in self._childs:
            child._init_sync_preferences()

    def _update_and_save(self, name, new):
        """Method called each time the value of a 'sync' preference is changed

        This method is called to update the default preference file when a
        'sync' preference is modified so that the right value is always stored
        even if the program does exit properly. This method is thread safe.

        Parameters
        ----------
        name : str
            Name of the update trait
        new : any
            New value of the trait

        Returns
        -------
        none
        """
        #simple check to avoid saving at init time
        if self._root._init_complete:
            self._pref_lock.acquire()
            self._preferences[name] = new
            self._pref_lock.release()
            self._save_preferences()

    def _save_preferences(self, filename = None):
        """Thread safe method to safe the preferences

        Private method implementing a thread safe procedure to save the
        preferences to an .ini file  which is either specified when the method
        is called or is the default file for the root node. This method
        contrary to the public method DOES NOT update the preferences from the
        associated traits.

        Parameters
        ----------
        filename : str, optional
            Path of the file to which preferences will be saved. If left to
            None, preferences will be saved to the default file of the root
            node.

        Returns
        -------
        none
        """
        if self._depth != 0:
            self._root._save_preferences()
        else:
            self._pref_lock.acquire()
            if filename is not None:
                #here I assume that the filename is right
                self._preferences.write(filename)
            else:
                self._preferences.write()
            self._pref_lock.release()

    def _update_prefs_from_traits(self):
        """Thread safe method updating the preference tree for the traits

        This method updates the values in the preference tree from the
        associated traits. Only 'async' value are updated as 'sync' ones are
        always right.

        Parameters
        ----------
        none

        Returns
        -------
        none
        """
        #update values for this class
        self._pref_lock.acquire()
        for name in self.traits(preference = 'async'):
            self._preferences[name] = str(self.get(name).values()[0])
        self._pref_lock.release()

        #ask childs to do the same
        for child in self._childs:
            child._update_prefs_from_traits()

    def _update_traits_from_prefs(self, all_traits = False):
        """Thread safe method using values from preferences to set traits

        This method updates the traits, which are preferences, using the values
        from the preference tree in a thread safe way. By default, 'sync'
        preferences are not updated.

        Parameters
        ----------
        all_traits : bool
            Boolean indicating whether or not 'sync' preferences should be
            updated

        Returns
        -------
        none
        """
        if all_traits is False:
            test = lambda x: x == 'async'
        else:
            test = lambda x: (x == 'async' or x == 'sync')

        #updating trait values from the preference tree where everything is
        # stored as strings
        for name, trait in self.traits(preference = test).iteritems():
            self._pref_lock.acquire()
            value = self._preferences[name]
            handler = trait.handler

            # If the trait type is 'Str' then we just take the raw value.
            if isinstance(handler, Str) or trait.is_str:
                pass

            # If the trait type is 'Unicode' then we convert the raw value.
            elif isinstance(handler, Unicode):
                value = unicode(value)

            # Otherwise, we eval it!
            else:
                try:
                    value = eval(value)

                # If the eval fails then there is probably a syntax error, but
                # we will let the handler validation throw the exception.
                except:
                    pass

            if handler.validate is not None:
                # Any traits have a validator of None.
                validated = handler.validate(self, name, value)
            else:
                validated = value

            self.trait_set(**{name : validated})
            self._pref_lock.release()

        # ask childs to do the same
        for child in self._childs:
            child._update_traits_from_prefs(all_traits)

    def _init_pref_view(self):
        """Method building the preference view if none is defined

        Method building a view to edit traits marked as preferences if none
        is defined in the subclass.
        """
        if self.trait_view('preference_view') is None:
            item_list = []
#            indice = 0
            for name in self.traits(preference = 'async').keys():
                item_list.append(Item(name))
#            for child in self._childs:
#                if child.merge_ui_with_parent:
#                    name = '_child'+str(indice)
#                    indice += 1
#                    self.add_trait('_child'+str(indice), child)
#                    item_list.append(Group(Item(name),
#                                           show_border = True,
#                                           label = child._name))
            aux_view = View(Group(item_list))
            self.trait_view('preference_view', aux_view)

#XXX old doc when a merge ui trait was supposed o exist
#             Attributes
#    ----------
#    merge_ui_with_parent : bool
#        Indicates whether or not the preference view should be merged with the
#        one from its parent. False by default.
#
#    All other attributes are private and doesn't have to be accessed in
#    subclasses
