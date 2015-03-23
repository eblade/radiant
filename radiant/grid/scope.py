#!/usr/bin/env python3


class Scope(object):
    def __init__(self):
        self._variables = {}
        self._listeners = {}

    def define(self, name, value=None, type=str):
        if not name in self._variables.keys():
            v = Variable(name, value, type)
            self._variables[name] = v
    
    def update(self, name, value):
        v = self._variables.get(name)
        if v is None:
            raise NameError("Not defined: " + name)
        v.update(value)

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
