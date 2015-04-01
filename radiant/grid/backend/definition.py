#!/usr/bin/env python


class ViewDefinition(object):
    data_type = "grid/view/entry"

    def __init__(self, d=None):
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
    data_type = "grid/item/entry"

    def __init__(self, d=None):
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
    data_type = "grid/document/entry"

    def __init__(self, d=None):
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
    data_type = "grid/column/entry"

    def __init__(self, d=None):
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
    data_type = "grid/variable/entry"

    def __init__(self, d=None):
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


class Feed(object):
    def __init__(self, entry_class, d=None):
        self.entry_class = entry_class
        self.data_type = entry_class.data_type.replace('/entry', '/feed')
        self.count = 0
        self.entries = []

        if d: self.from_dict(d)

    def to_dict(self):
        return {
            "data-type": self.data_type,
            "count": self.count,
            "entries": [entry.to_dict() for entry in self.entries]
        }

    def from_dict(self, d):
        assert d.get('data-type') == self.data_type
        self.count = d.get('count', 0)
        self.entries = [self.entry_class(entry) for entry in d.get('entries', [])]

