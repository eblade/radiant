#!/usr/bin/env python

"""
The *Definition* module contains object wrappers of the various
*data-types* found in Radiant Grids. Those are:

- :class:`ViewDefinition`
- :class:`ItemDefinition`
- :class:`DocumentDefinition`
- :class:`ColumnDefinition`
- :class:`VariableDefinition`
- :class:`DataDefinition`
- :class:`Feed`

.. note::
    
    Each entry in "Variables" list for each class has a name 
    [*emphasized within brackets*]. This is the key in the *dict*-
    representation of it's data, which would be used when
    serializing to JSON.
"""


class ViewDefinition(object):
    """
    Defines a View within a Workspace. A View describes a graphical representation
    of the data in the Workspace using *items*. Items have various properties
    depending on what type of item they are. See :class:`ItemDefinition`.

    :cvar str name: [*name*] Workspace-unique name of this View
    :cvar list items: [*items*] List of :class:`ItemDefinition`
    """
    data_type = "grid/view/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.name = None
        self.items = {}
        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "name": self.name,
            "items": [item.to_dict() for item in self.items.values()],
        }

    def from_dict(self, d):
        assert d.get("data-type") == self.data_type
        self.name = d["name"]
        items = [ItemDefinition(item) for item in d.get("items", [])]
        self.items = {item.name: item for item in items}
        

class ItemDefinition(object):
    """
    Defines a graphical *Item* in a *View* (:class:`ViewDefinition`). The ``item_type`` can be one of:

    - ``Label`` - A label with an optional title
    - ``Table`` - A table bound to a document

    :cvar str item_type: [*item-type*] The type of item this is
    :cvar str name: [*name*] View-unique name of this Item
    :cvar dict properties: [*properties*] Various properties for this item
    :cvar list position: [*position*] Two or four values describing the position, either as 
                         (x, y) or (x1, y1, x2, y2) depending on item type
    """
    data_type = "grid/item/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.item_type = None
        self.name = None
        self.properties = {}
        self.position = None

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "item-type": self.item_type,
            "name": self.name,
            "properties": self.properties,
            "position": self.position,
        }

    def from_dict(self, d):
        assert d.get("data-type") == self.data_type
        self.item_type = d['item-type']
        self.name = d['name']
        self.properties = d['properties']
        self.position = d['position']


class DocumentDefinition(object):
    """
    Defines a Document within a Workspace. A Document describes a
    table in a database that can hold data. The columns are defined
    by :class:`ColumnDefinition` objects.

    :cvar str name: [*name*] Workspace-unique name of this View
    :cvar dict columns: [*columns*] List of :class:`ColumnDefinition`
    """
    data_type = "grid/document/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.name = None
        self.columns = {}
        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "name": self.name,
            "columns": [column.to_dict() for column in self.columns.values()]
        }

    def from_dict(self, d):
        assert d.get("data-type") == self.data_type
        self.name = d["name"]
        columns = [ColumnDefinition(column) for column in d.get("columns", [])]
        self.columns = {column.name: column for column in columns}

class ColumnDefinition(object):
    """
    Defines a Column within a Document. The properties of the
    ColumnDefinition are meant to describe a database column.

    :cvar str name: [*name*] Document-unique name of this Column
    :cvar str type_name: [*type-name*] Database type (``INTEGER``, ``TEXT``, ``REAL``, ``BLOB``)
    :cvar int type_size: [*type-size*] Database type size (if applicable, else ``None``)
    :cvar bool primary_key: [*primary-key*] Column is the *primary key* (default ``False``)
    :cvar str default: [*default*] Use this default value (default ``None``)
    :cvar bool auto_increment: [*auto-increment*] Column is the *auto incrementing* (default ``False``)
    :cvar bool unique: [*unique*] Column has a *unique constraint* (default ``False``)
    """
    data_type = "grid/column/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.name = None
        self.type_name = None
        self.type_size = None
        self.primary_key = False
        self.default = None
        self.auto_increment = False
        self.unique = False

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "name": self.name,
            "type-name": self.type_name,
            "type-size": self.type_size,
            "primary-key": self.primary_key,
            "default": self.default,
            "auto-increment": self.auto_increment,
            "unique": self.unique
        }

    def from_dict(self, d):
        assert d.get('data-type') == self.data_type
        self.name = d['name']
        self.type_name = d['type-name']
        self.type_size = d.get('type-size')
        self.primary_key = d.get('primary-key', False)
        self.default = d.get('default')
        self.auto_increment = d.get('auto_increment', False)
        self.unique = d.get('unique', False)


class VariableDefinition(object):
    """
    Defines a Variable within a Workspace. Variables typically 
    have dot-separated names.

    :cvar str name: [*name*] Workspace-unique name of this Variable
    :cvar str type: [*type*] Type of the variable (:class:`str` (default), :class:`int`, 
                    :class:`float`, :class:`bool`)
    :cvar str value: [*value*] The value of the Variable
    """
    data_type = "grid/variable/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.name = None
        self.type = 'str'
        self.value = None

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "name": self.name,
            "type": self.type,
            "value": self.value
        }

    def from_dict(self, d):
        assert d.get('data-type') == self.data_type
        self.name = d['name']
        self.type = d.get('type', 'str')
        self.value = d.get('value')


class DataDefinition(object):
    """
    Defines a Row of Data within a Document. 

    :cvar dict data: [*data*] A dict with the values of the columns
    """
    data_type = "grid/data/entry"
    """ [*data-type*] """

    def __init__(self, d=None):
        """
        Constructor.

        :param dict d: Optional dictionary to import
        """
        self.data = None

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "data": self.data
        }

    def from_dict(self, d):
        self.data = dict(d)


class Feed(object):
    def __init__(self, entry_class, d=None, data_type=None):
        """
        Constructor.

        :param class entry_class: The class used for the entries of this feed
        :param dict d: Optional dictionary to import
        :param str data_type: Optional *data-type* to use, overriding ``entry_class.data_type``
        """
        self.entry_class = entry_class
        self.data_type = data_type or entry_class.data_type.replace('/entry', '/feed')
        self.workspace = None
        self.start = 0
        self.count = 0
        self.page_size = 0
        self.entries = []

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "workspace": self.workspace,
            "start": self.start,
            "count": self.count,
            "page-size": self.page_size,
            "entries": [entry.to_dict() for entry in self.entries]
        }

    def from_dict(self, d):
        assert d.get('data-type') == self.data_type
        self.workspace = d.get('workspace')
        self.start = d.get('start', 0)
        self.count = d.get('count', 0)
        self.page_size = d.get('page-size', 0)
        self.entries = [self.entry_class(entry) for entry in d.get('entries', [])]
