#!/usr/bin/env python3

from ..tk import tk, ttk, Dialog
from .item import ItemType, Label, Table
from .scope import Scope
from .backend.definition import ViewDefinition, ItemDefinition

PADDING_X=10
PADDING_Y=10
GRID_SIZE=25


class View(ttk.Frame):
    def __init__(self, parent, name):
        ttk.Frame.__init__(self, parent)
        self.parent=parent
        self.workspace = parent.workspace
        self.name = name
        self.original_name = name
        self.pack(fill=tk.BOTH, expand=1)
        self.grid_size = GRID_SIZE
        self.padding = (PADDING_X, PADDING_Y)

        # Styling the background
        style = ttk.Style()
        style.configure("TFrame", background="#ccc") 

        # Canvas
        self.canvas = tk.Canvas(self, 
            background="white", 
            width=800, height=600
        )
        self.configure(scrollregion=self.canvas.bbox("all"))

        # Placing Canvas
        self.canvas.place(x=0, y=0)

        # Declare object and title variable
        self.workspace.scope.define(self.name + '.title', value='untitled')
        self.items = {}
        self._selected_name = None

        # Load the View Definition from the Database
        self.from_definition(self.parent.workspace.adapter.get_view(name))

        # Key bindings
        self.canvas.bind("<F2>", self.on_edit_text)
        self.canvas.bind("<F3>", self.on_edit)
        self.canvas.bind("<Down>", self.on_down)
        self.canvas.bind("<Up>", self.on_up)
        self.canvas.bind("<Left>", self.on_left)
        self.canvas.bind("<Right>", self.on_right)
        self.canvas.focus_set()

    def from_definition(self, definition):
        # Load View from a ViewDefinition
        self.name = self.original_name = definition.name
        for item in definition.items.values():
            self.add_item(
                item.name,
                ItemType(item.item_type),
                item.position,
                **(item.properties)
            )

    def to_definition(self):
        # Export the current view to a ViewDefinition
        view_def = ViewDefinition()
        view_def.name = self.name

        for item in self.items.values():
            view_def.items[item.name] = ItemDefinition(item.to_dict())

        return view_def

    def save_view(self):
        # Save the view to the workspace
        self.parent.workspace.adapter.edit_view(
            self.original_name,
            self.to_definition()
        )

    def add_item(self, name, klass, position, **options):
        # Create item
        item = klass(self)
        item.config(**options)
        item.create(name, position)

        # Keep track
        self.items[name] = item

    def select(self, name):
        # Deselect the currently selected item
        if self._selected_name is not None:
            current = self.items.get(self._selected_name)
            if current is not None:
                current.deselect()

        # Set the new selected variable
        self._selected_name = name
        
        # If name is None, there is no selection
        if name is None:
            return

        # Fetch the item to select
        new = self.items.get(self._selected_name)

        # The item might have dissappeared
        if new is None:
            self._selected_name = None
            return

        # Select the new item
        new.select()

    def deselect(self):
        self._select_name = None

    def snap(self, position):
        x, y = position
        grid_size = self.grid_size
        padding_x, padding_y = self.padding
        x = int(grid_size * round(float(x-padding_x)/grid_size))+padding_x
        y = int(grid_size * round(float(y-padding_y)/grid_size))+padding_y
        x = max(x, padding_x)
        y = max(y, padding_y)

        return (x, y)

    def on_edit_text(self, event):
        if self._selected_name is None:
            return

        item = self.items.get(self._selected_name)

        if item is None:
            return

        item.on_edit_text()

    def on_edit(self, event):
        if self._selected_name is None:
            return

        item = self.items.get(self._selected_name)

        if item is None:
            return

        item.on_edit()

    def on_save_view(self, *args):
        self.save_view()

    def on_create_label(self, *args):
        d = Dialog(self, "Create Label", value="label",
                   focus=self.canvas)
        if not d.cancelled:
            self.add_item(d.value, Label, self.padding)
            self.select(d.value)

    def on_create_table(self, *args):
        d = Dialog(self, "Create Table", value="table",
                   focus=self.canvas)
        if not d.cancelled:
            self.add_item(d.value, Table, self.padding)
            self.select(d.value)

    def on_down(self, event):
        if self._selected_name is not None:
            if event.state == 4: # Ctrl
                self.items[self._selected_name].move(0, self.grid_size)

    def on_up(self, event):
        if self._selected_name is not None:
            if event.state == 4: # Ctrl
                self.items[self._selected_name].move(0, -self.grid_size)

    def on_left(self, event):
        if self._selected_name is not None:
            if event.state == 4: # Ctrl
                self.items[self._selected_name].move(-self.grid_size, 0)

    def on_right(self, event):
        if self._selected_name is not None:
            if event.state == 4: # Ctrl
                self.items[self._selected_name].move(self.grid_size, 0)
