#!/usr/bin/env python3


class DocumentBinding(object):
    """
    Provides editing and listening capabilities to a 
    ``:class:radiant.grid.definition.DocumentDefinition`` using a
    ``:class:radiant.grid.adapter.*``.
    """

    def __init__(self, adapter, document):
        self.adapter = adapter
        self.document = document

    def listen(self, listener, callback):
        pass

    def forget(self, listener):
        pass

    def query(self, columns, start, count):
        data = adapter.get_rows(self.document.name, start, count)
