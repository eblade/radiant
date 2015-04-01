#!/usr/bin/env python

import sqlite3
import re
import os
import json
from sqlite3 import IntegrityError, OperationalError
from traceback import format_exc

EXTENSION = '.grid'


class GridBackend(object):
    def __init__(self, directory):
        self.directory = directory

    def get_connection(self, workspace):
        workspace = Column.validate_name(workspace) + EXTENSION
        db = sqlite3.connect(os.path.join(self.directory, workspace))
        db.row_factory = sqlite3.Row
        return db

    def create_workspace(self, workspace):
        db = self.get_connection(workspace)
        
        try:
            db.execute("CREATE TABLE _grid_docs (" +
                       "name TEXT(128) PRIMARY KEY, " +
                       "read_token TEXT(256), " +
                       "write_token TEXT(256), " +
                       "create_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "update_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "data_model BLOB)"
                      )
            db.execute("CREATE TABLE _grid_views (" +
                       "name TEXT(128) PRIMARY KEY, " +
                       "read_token TEXT(256), " +
                       "write_token TEXT(256), " +
                       "create_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "update_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "data_model BLOB)"
                      )
            db.execute("CREATE TABLE _grid_vars (" +
                       "name TEXT(128) PRIMARY KEY, " +
                       "create_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "update_ts INTEGER DEFAULT (strftime('%s', 'now')), " +
                       "type TEXT(32) DEFAULT ('str'), " +
                       "value TEXT(2048))"
                      )
            db.execute("CREATE TABLE _grid_tokens (" +
                       "has TEXT(128) PRIMARY KEY, " +
                       "gets TEXT(128), " +
                       "expires INTEGER)"
                      )
            db.commit()
        except OperationalError as e:
            db.rollback()
            raise DatabaseError("Workspace exists", e, format_exc())
        finally:
            db.close()

    def get_workspaces(self):
        workspaces = []
        for f in os.listdir(self.directory):
            if not f.endswith(EXTENSION):
                continue
            if not os.path.isfile(os.path.join(self.directory, f)):
                continue
            workspaces.append(f[:-len(EXTENSION)])
        return {
            'data-type': 'grid/workspace/enum',
            'workspace-names': workspaces
        }

    def get_workspace(self, workspace):
        documents = self._fetch_documents(workspace, models=False)
        return {
            'data-type': 'grid/workspace/entry',
            'name': workspace,
            'document-names': documents
        }

    def create_view(self, workspace, view):
        name = Column.validate_name(view.get('name'))
        assert name is not None

        db = self.get_connection(workspace)
        try:
            db.execute("INSERT INTO _grid_views " +
                       "(name, read_token, write_token, data_model) " +
                       "VALUES (?, ?, ?, ?)",
                       (name, "*", "*", json.dumps(view)))
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError("View exists", e, format_exc())
        finally:
            db.close()

    def edit_view(self, workspace, view, view_model):
        old_name = Column.validate_name(view)
        new_name = Column.validate_name(view_model.get('name'))
        assert old_name is not None
        assert new_name is not None
        
        db = self.get_connection(workspace)
        try:
            db.execute("UPDATE _grid_views " +
                       "SET name=?, update_ts=strftime('%s', 'now'), data_model=? " +
                       "WHERE name=?",
                       (new_name, json.dumps(view_model), old_name))
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError("View exists", e, format_exc())
        finally:
            db.close()

    def get_view(self, workspace, view):
        views = self._fetch_views(workspace, view=view)
        if len(views) == 0:
            raise DatabaseError("No such view")
        data = views.pop()
        data['data-type'] = 'grid/view/entry'
        return data

    def get_views_in_workspace(self, workspace):
        views = self._fetch_views(workspace)
        return {
            'data-type': 'grid/grid/feed',
            'workspace': workspace,
            'entries': views,
            'count': len(views),
        }

    def create_variable(self, workspace, variable):
        name = Column.validate_variable_name(variable.get('name'))
        assert name is not None

        db = self.get_connection(workspace)
        try:
            db.execute("INSERT INTO _grid_vars " + 
                       "(name, type, value) " +
                       "VALUES (?, ?, ?)", 
                       (name, variable.get('type', 'str'), variable.get('value')))
        
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError("Variable exists", e, format_exc())
        finally:
            db.close()

    def edit_variable(self, workspace, variable, data):
        old_name = Column.validate_variable_name(variable)
        new_name = Column.validate_variable_name(data.get('name'))
        assert old_name is not None
        assert new_name is not None
        
        db = self.get_connection(workspace)
        try:
            db.execute("UPDATE _grid_vars " +
                       "SET name=?, update_ts=strftime('%s', 'now'), value=? " +
                       "WHERE name=?",
                       (new_name, data.get('value'), old_name))
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError("Variable exists", e, format_exc())
        finally:
            db.close()

    def get_variable(self, workspace, variable):
        name = Column.validata_variable_name(variable)
        assert name is not None

        variables = self._fetch_variables(workspace, variable=name)
        if len(variables) == 0:
            raise DatabaseError("No such variable")
        variable = variables.pop()
        return variable

    def get_variables_in_workspace(self, workspace):
        variables = self._fetch_variables(workspace)
        return {
            'data-type': 'grid/variable/feed',
            'workspace': workspace,
            'entries': variables,
            'count': len(variables),
        }

    def create_document(self, workspace, document):
        name = Column.validate_name(document.get('name'))
        columns = document.get('columns')
        assert name is not None
        assert columns is not None

        if name.startswith('_'):
            raise ValueError('Names starting with _ are reserved for internals')

        # Prepare Column SQL
        column_sql = []
        for cdata in columns:
            column = Column(cdata)
            column_sql.append(column.sql())

        db = self.get_connection(workspace)
        try:
            db.execute("INSERT INTO _grid_docs " + 
                       "(name, read_token, write_token, data_model) " +
                       "VALUES (?, ?, ?, ?)", 
                       (name, "*", "*", json.dumps(document)))
        
            db.execute("CREATE TABLE " + name + " (" + ', '.join(column_sql) + ')')
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise DatabaseError("Document exists", e, format_exc())
        finally:
            db.close()

    def get_document(self, workspace, document):
        documents = self._fetch_documents(workspace, document=document)
        if len(documents) == 0:
            raise DatabaseError("No such document")
        data = documents.pop()
        data['data-type'] = 'grid/document/entry'
        return data

    def get_documents_in_workspace(self, workspace):
        documents = self._fetch_documents(workspace)
        if len(documents) == 0:
            raise DatabaseError("No such document")
        return {
            'data-type': 'grid/document/feed',
            'workspace': workspace,
            'entries': documents,
            'count': len(documents),
        }

    def delete_document(self, workspace, document):
        if document.startswith('_'):
            raise ValueError('Names starting with _ are reserved for internals')
        document = Column.validate_name(document)

        db = self.get_connection(workspace)
        try:
            db.execute("DELETE FROM _grid_docs WHERE name=?", (document,))
            db.execute("DROP TABLE " + document)
        except OperationalError as e:
            db.rollback()
            raise DatabaseError("Could not delete document", e, format_exc())
        finally:
            db.close()

    def edit_rows(self, workspace, document, data):
        assert data.get('data-type') == 'grid/instruction/feed'

        instruction_result = self._edit_rows(
            workspace, document, 
            [Instruction(i) for i in data.get('instructions', [])]
        )

        return {
            'data-type': 'grid/instruction/feed',
            'instructions': [instruction.to_dict() 
                            for instruction in instruction_result]
        }

    def edit_row(self, workspace, document, data):
        assert data.get('data-type') == 'grid/instruction/entry'

        instruction_result = self._edit_rows(
            workspace, document, 
            [Instruction(data)]
        )[0]

        return instruction_result.to_dict()

    def get_rows(self, workspace, document, start, count):
        if document.startswith('_'):
            raise ValueError('Names starting with _ are reserved for internals')
        document = Column.validate_name(document)
        start = int(start)
        count = int(count)

        rows = []
        db = self.get_connection(workspace)
        try:
            cur = db.execute("SELECT * FROM " + document + 
                             " LIMIT ? OFFSET ?", (count, start))
            rows = cur.fetchall()
        finally:
            db.close()

        return {
            'data-type': 'grid/data/feed',
            'start': start,
            'count': len(rows),
            'page-size': count,
            'rows': [{k: row[k] for k in row.keys()} for row in rows],
        }

    def _edit_rows(self, workspace, document, instructions):
        if document.startswith('_'):
            raise ValueError('Names starting with _ are reserved for internals')
        document = Column.validate_name(document)

        db = self.get_connection(workspace)
        try:
            for instruction in instructions:
                instruction.perform(db, document)
        finally:
            db.close()

        return instructions

    def _fetch_views(self, workspace, view=None, models=True):
        view = Column.validate_name(view)
        db = self.get_connection(workspace)

        views = []
        column = 'data_model' if models else 'name'
        try:
            if view is None:
                c = db.execute("SELECT " + column + " FROM _grid_views")
            else:
                c = db.execute("SELECT " + column + " FROM _grid_views WHERE name=?",
                               (view,))

            for row in c:
                if models:
                    views.append(json.loads(row['data_model']))
                else:
                    views.append(row['name'])

        except OperationalError as e:
            raise DatabaseError("Invalid database", e, format_exc())
        finally:
            db.close()
        return views

    def _fetch_documents(self, workspace, document=None, models=True):
        document = Column.validate_name(document)
        db = self.get_connection(workspace)
        
        documents = []
        column = 'data_model' if models else 'name'
        try:
            if document is None:
                c = db.execute("SELECT " + column + " FROM _grid_docs")
            else:
                c = db.execute("SELECT " + column + " FROM _grid_docs WHERE name=?",
                               (document,))
            for row in c:
                if models:
                    documents.append(json.loads(row['data_model']))
                else:
                    documents.append(row['name'])

        except OperationalError as e:
            raise DatabaseError("Invalid database", e, format_exc())
        finally:
            db.close()
        return documents
        
    def _fetch_variables(self, workspace, variable=None):
        variable = Column.validate_variable_name(variable)
        db = self.get_connection(workspace)
        
        variables = []
        column = 'name, type, update_ts, value'
        try:
            if variable is None:
                c = db.execute("SELECT " + column + " FROM _grid_vars")
            else:
                c = db.execute("SELECT " + column + " FROM _grid_vars WHERE name=?",
                               (variable,))
            for row in c:
                variables.append({
                    "data-type": "grid/variable/entry",
                    "name": row['name'],
                    "type": row['type'],
                    "update-ts": row['update_ts'],
                    "value": row['value']
                })

        except OperationalError as e:
            raise DatabaseError("Invalid database", e, format_exc())
        finally:
            db.close()
        return variables


class Column(object):
    cleaner = re.compile(r'[^A-Za-z0-9_]+')
    variable_cleaner = re.compile(r'[^A-Za-z0-9_\.]+')

    def __init__(self, data=None):
        self.name = None
        self.type_name = None
        self.type_size = None
        self.primary_key = False
        self.default = None
        self.auto_increment = False
        self.unique = False
        self._has_default_data = False

        if data is not None:
            self.use(data)

    def use(self, data):
        self.name = Column.validate_name(data.get('name'))
        self.type_name = Column.validate_name(data.get('type-name'))
        self.type_size = Column.validate_int(data.get('type-size'))
        self.primary_key = Column.validate_bool(data.get('primary-key', False))
        self.default = Column.validate_name(data.get('default'))
        self.auto_increment = Column.validate_bool(data.get('auto-increment', False))
        self.unique = Column.validate_bool(data.get('unique', False))
        self.null = Column.validate_bool(data.get('null'), none_is_ok=True)

        if self.default == 'NOW':
            self._has_default_data = False
        elif self.default is not None:
            self._has_default_data = True

        assert self.name is not None
        assert self.type_name is not None
        self.type_name = self.type_name.upper()
        assert self.type_name in ("INTEGER", "TEXT", "REAL", "BLOB")
        assert not (self.primary_key and self.default)
        assert not (self.primary_key and self.unique)
        assert not (self.unique and self.has_default_data)
        assert not (self.primary_key and self.null is True)
        assert not (self.unique and self.null is True)
    
    @property
    def has_default_data(self):
        return self._has_default_data

    def sql(self):
        parts = [self.name]

        if self.type_size is None:
            parts.append(self.type_name)
        else:
            parts.append('%s(%i)' % (self.type_name, self.type_size))

        if self.primary_key:
            parts.append('PRIMARY KEY')

        if self.unique:
            parts.append('UNIQUE')

        if self.null is True:
            parts.append('NULL')
        elif self.null is False:
            parts.append('NOT NULL')

        if self.default == 'NOW':
            parts.append(r"DEFAULT (strftime('%s', 'now'))")
        elif self.has_default_data:
            parts.append(r"DEFAULT '%s'" % self.default)
        
        return ' '.join(parts)

    @classmethod
    def validate_name(cls, expr):
        if expr is None:
            return None
        cleaned = cls.cleaner.sub('', expr)
        if cleaned != expr:
            raise ValueError("Only [A-Za-z0-9_] allowed in names")
        return expr
        
    @classmethod
    def validate_variable_name(cls, expr):
        if expr is None:
            return None
        cleaned = cls.variable_cleaner.sub('', expr)
        if cleaned != expr:
            raise ValueError("Only [A-Za-z0-9_\.] allowed in variable names")
        return expr

    @classmethod
    def validate_int(cls, expr):
        if expr is None:
            return None
        return int(expr)

    @classmethod
    def validate_bool(cls, expr, none_is_ok=False):
        if expr is None and none_is_ok:
            return None
        if not expr in (True, False):
            raise ValueError("Only True and False allowed in bools")
        return expr


class Table(object):
    def __init__(self, data):
        self.name = data.get('name')
        self.columns = [Column(c) for c in data.get('columns', [])]
        self.primary_key = self.get_primary_key()

    def get_primary_key(self):
        for column in self.columns:
            if column.primary_key:
                return column.name

class Instruction(object):
    def __init__(self, data):
        self.mode = data.get('mode', 'insert')
        self.is_insert = self.mode == 'insert'
        self.is_update = self.mode == 'update'
        self.is_delete = self.mode == 'delete'
        self.values = data.get('values', {})
        self.where = data.get('where', {})
        self.status = None
        self.affected_rows = 0

    def __repr__(self):
        return "<Instruction {0}>".format(self.mode)
    
    def to_dict(self):
        return {
            'data-type': 'grid/instruction/entry',
            'mode': self.mode,
            'values': self.values,
            'where': self.where,
            'status': self.status,
            'affected-rows': self.affected_rows,
        }

    def get_value(self, column):
        return self.values.get(column)
    
    def get_value_lists(self):
        columns = []
        values = []
        for k, v in self.values.items():
            columns.append(k)
            values.append(v)
        return columns, values

    def get_where_lists(self):
        columns = []
        values = []
        for k, v in self.where.items():
            columns.append(k)
            values.append(v)
        return columns, values

    def perform(self, db, document):
        if self.is_insert:
            self._perform_insert(db, document)
        elif self.is_update:
            self._perform_update(db, document)
        elif self.is_delete:
            self._perform_delete(db, document)

    def _perform_insert(self, db, document):
        try:
            columns, values = self.get_value_lists()
            cur = db.cursor()
            cur.execute("INSERT INTO " + document + 
                        "(" + ', '.join(columns) + ") " +
                        "VALUES (" + ', '.join(['?'] * len(values)) + ")",
                        values)
            self.affected_rows = cur.rowcount
            db.commit()
            self.status = True
        finally:
            self.status = False if self.status is None else self.status

    def _perform_update(self, db, document):
        try:
            columns, values = self.get_value_lists()
            where_columns, where_values = self.get_where_lists()
            cur = db.cursor()
            cur.execute("UPDATE " + document + 
                        " SET " + ", ".join([c+"=?" for c in columns]) +
                        (
                            (" WHERE " + ", ".join([c+"=?" for c in where_columns])
                             if len(where_columns) else "")
                        )
                        , values + where_values)
            self.affected_rows = cur.rowcount
            db.commit()
            self.status = True
        finally:
            self.status = False if self.status is None else self.status

    def _perform_delete(self, db, document):
        try:
            where_columns, where_values = self.get_where_lists()
            cur = db.cursor()
            cur.execute("DELETE FROM " + document + 
                        (
                            (" WHERE " + ", ".join([c+"=?" for c in where_columns])
                             if len(where_columns) else "")
                        )
                        , where_values)
            self.affected_rows = cur.rowcount
            db.commit()
            self.status = True
        finally:
            self.status = False if self.status is None else self.status

class DatabaseError(Exception):
    def __init__(self, message=None, exception=None, traceback=None):
        self.message = message
        self.exception = exception
        self.traceback = traceback
