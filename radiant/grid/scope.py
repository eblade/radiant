#!/usr/bin/env python3

from .backend.definition import Feed, VariableDefinition


class Scope(object):
    def __init__(self, adapter):
        self.adapter = adapter
        self._variables = {}
        self._listeners = {}
        variables = self.adapter.get_variables_in_workspace()
        for variable in variables.entries:
            self._variables[variable.name] = Variable.from_definition(variable)

    def define(self, name, value=None, type=str):
        if not name in self._variables.keys():
            v = Variable(name, value, type)
            self._variables[name] = v
            try:
                self.adapter.create_variable(v.to_definition())
            except NameError:
                pass
    
    def update(self, name, value):
        v = self._variables.get(name)
        if v is None:
            raise NameError("Not defined: " + name)
        v.update(value)
        self.adapter.edit_variable(name, v.to_definition())

    def listen(self, listener, tag, name, callback):
        v = self._variables.get(name)
        if v is None:
            raise NameError("Not defined: " + name)
        tag = str(id(listener)) + tag
        l = v.listen(tag, callback)
        self._listeners[tag] = v

    def nevermind(self, listener, tag):
        tag = str(id(listener)) + tag
        v = self._listeners.get(tag)
        if v is not None:
            v.forget(tag)
            self._listeners.pop(tag)

    def get(self, name):
        v = self._variables.get(name)
        if v is None:
            raise NameError("Not defined: " + name)
        return v.value
        

class Variable(object):
    def __init__(self, name, value, type):
        self.name = name
        self.type = type
        self.listeners = {}
        self.value = value
    
    def update(self, value):
        self.value = self.type(value)
        for listener in self.listeners.values():
            try:
                listener(value)
            except Exception as e:
                print("Error: " + str(e))

    def listen(self, tag, callback):
        self.listeners[tag] = callback

    def forget(self, tag):
        self.listeners.pop(tag)

    def to_dict(self):
        return {
            "data-type": "grid/variable/entry",
            "name": self.name,
            "type": self.type.__name__,
            "value": self.value
        }

    def to_definition(self):
        return VariableDefinition(self.to_dict())

    @classmethod
    def from_definition(cls, definition):
        if definition.type == 'str':
            type = str
        elif definition.type == 'int':
            type = int
        elif definition.type == 'float':
            type = float
        else:
            type = str
        return cls(definition.name, definition.value, type)
