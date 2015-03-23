#!/usr/bin/env python3

from ..tk import tk, ttk
from .item import Label, Table
from .scope import Scope

PADDING_X=10
PADDING_Y=10
GRID_SIZE=25


class View(ttk.Frame):
    def __init__(self, parent, title):
        ttk.Frame.__init__(self, parent)
        self.parent=parent
        self.title = tk.StringVar()
        self.title.set(title)
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

        # Declare object and variable dicts
        self.scope = Scope()
        self.scope.define('title', value='untitled')
        self.items = {}
        self.variables = {}
        self._selected_name = None

        # Title Label
        self.add_item("title", Label, self.padding,
            font=("Helvetica", 16),
            color="#aaa",
            show_title=False,
            editable=True,
            variable="title"
        )

        # Test
        self.add_item("test1", Label, (10, 110),
            font=("Helvetica", 26),
            color="red",
            title="Another title",
            text="Another text",
        )
        self.add_item("test2", Label, (10, 210),
            font=("Helvetica", 26),
            color="green",
        )
        self.add_item("test3", Label, (10, 310),
            font=("Helvetica", 72),
            color="blue",
            width=0,
            editable=True,
            variable="title",
        )
        self.add_item("test_table", Table, (220, 35))

        self.items['test2'].text = 'Green'
        self.items['test3'].text = 'Large Blue'

        # Key bindings
        self.canvas.bind("<F2>", self.on_edit_text)
        self.canvas.focus_set()

    def add_item(self, name, klass, position, **options):
        # Create object
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

        item.on_edit()
