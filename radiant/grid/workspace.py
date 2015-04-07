#!/usr/bin/env python3

from .backend.definition import ViewDefinition, ItemDefinition
from .scope import Scope
from .document import DocumentBinding


class Workspace(object):
    def __init__(self, workspace, server=None, token=None, directory=None):
        self.workspace = workspace

        if directory:
            self.init_local(directory)
        elif server and token:
            self.init_http(server, token)
        else:
            raise ValueError("Need either directory or server+token")

        if workspace is not None:
            try:
                self.adapter.open_workspace(workspace)
                self.scope = Scope(self.adapter)
            except NameError:
                self.create_workspace(workspace)

    def init_local(self, directory):
        from .adapter import LocalAdapter
        self.adapter = LocalAdapter(directory)

    def init_http(self, server, token):
        from .adapter import HttpAdapter
        self.adapter = HttpAdapter(server, token)
    
    def create_workspace(self, workspace):
        self.adapter.create_workspace(workspace)
        self.scope = Scope(self.adapter)

        # Create main view with a title label
        view = ViewDefinition()
        view.name = "main"
        title = ItemDefinition()
        title.item_type = "Label"
        title.name = "title"
        title.properties = {
            "font": ("Helvetica", 16),
            "color": "#aaa",
            "show_title": False,
            "editable": True,
            "variable": "main.title"
        }
        title.position = (10, 10)
        view.items = {
            "title": title
        }

        self.adapter.create_view(view)

    def get_document_binding(self, document_name):
        document = self.adapter.get_document(document_name)
        return DocumentBinding(self.adapter, document)
