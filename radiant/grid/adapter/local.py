#!/usr/bin/env python3

import os
from ..backend import GridBackend, DatabaseError
from ..backend.definition import Feed,\
    ViewDefinition, VariableDefinition, DataDefinition

class LocalAdapter(object):
    def __init__(self, directory):
        self.backend = GridBackend(directory)
        self.workspace = None

    ### Workspace ###

    def open_workspace(self, workspace):
        try:
            self.backend.get_workspace(workspace)
            self.workspace = workspace
        except DatabaseError:
            raise NameError("Workspace not found")
    
    def create_workspace(self, workspace):
        self.backend.create_workspace(workspace)
        self.workspace = workspace

    ### VIEW DEFINITION ###

    def create_view(self, view):
        self.backend.create_view(self.workspace, view.to_dict())

    def edit_view(self, name, view):
        self.backend.edit_view(self.workspace, name, view.to_dict())

    def get_view(self, view):
        return ViewDefinition(self.backend.get_view(self.workspace, view))

    ### VARIABLE ###

    def create_variable(self, variable):
        try:
            self.backend.create_variable(self.workspace, variable.to_dict())
        except DatabaseError:
            raise NameError("Variable exists")
            
    def edit_variable(self, name, variable):
        try:
            self.backend.edit_variable(self.workspace, name, variable.to_dict())
        except DatabaseError:
            raise NameError("Variable exists")
        
    def get_variable(self, name):
        try:
            return VariableDefintion(
                self.backend.get_variable(self.workspace, name))
        except DatabaseError:
            raise NameError("Variable does not exist")

    def get_variables(self):
        return Feed(VariableDefinition,
            self.backend.get_variables(self.workspace))

    ### DOCUMENT ### 

    def create_document(self, document):
        self.backend.create_document(self.workspace, document.to_dict())

    def get_document(self, name):
        try:
            document = self.backend.get_document(self.workspace, name)
        except DatabaseError:
            raise NameError("Document does not exist")

    def enum_documents(self):
        return Feed(str, data_type="grid/document/enum",
            d=self.backend.enum_documents(self.workspace))
        

    ### ROWS ###

    def get_rows(self, document_name, start, count):
        return Feed(DataDefinition,
            self.backend.get_rows(document_name, start, count))
