#!/usr/bin/env python3

from ..tk import tk, ttk
from .view import View
from .workspace import Workspace


class GridApplication(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent=parent

        self.parent.title('Grids')
        self.parent.geometry('800x600+200+200')
        self.pack(fill=tk.BOTH, expand=1)

        # Set up Workspace
        self.workspace = Workspace(
            directory="/tmp",
            workspace="test",
        )
        
        # Load the main view
        self.views = []
        self.current_view = None
        self.load_view("main")

        # Create Menus
        self.menu = tk.Menu(self.parent)

        # Workspace Menu
        workspace_menu = tk.Menu(self.menu, tearoff=False)
        workspace_menu.add_command(
            label="Select Workspace..",
            command=None,
            underline=8,
        )
        workspace_menu.add_separator()
        workspace_menu.add_command(
            label="Quit",
            command=self.quit,
            underline=0,
            accelerator="Ctrl+Q"
        )
        self.bind_all("<Control-q>", self.on_quit)
        self.menu.add_cascade(
            label="Workspace",
            menu=workspace_menu,
            underline=0
        )

        # View Menu
        view_menu = tk.Menu(self.menu, tearoff=False)
        view_menu.add_command(
            label="Save View",
            command=self.on_save_view,
            underline=0,
            accelerator="Ctrl+S"
        )
        self.bind_all("<Control-s>", self.on_save_view)
        view_menu.add_command(
            label="Export to PostScript",
            command=self.on_postscript_view,
            underline=1,
        )
        self.menu.add_cascade(
            label="View",
            menu=view_menu,
            underline=0
        )

        # Item Menu
        item_menu = tk.Menu(self.menu, tearoff=False)
        item_menu.add_command(
            label="Create Label",
            command=self.on_create_label,
            underline=7,
            accelerator="Ctrl+L"
        )
        self.bind_all("<Control-l>", self.on_create_label)
        item_menu.add_command(
            label="Create Table",
            command=self.on_create_table,
            underline=7,
            accelerator="Ctrl+T"
        )
        self.bind_all("<Control-t>", self.on_create_table)
        self.menu.add_cascade(
            label="Item",
            menu=item_menu,
            underline=0
        )

        self.parent.config(menu=self.menu)

        self.parent.protocol('WM_DELETE_WINDOW', self.quit)

    def create_menu(self, *menus):
        self.menu=tk.Menu(self.parent)
        
        for menu_data in menus:
            widget = self._create_menu(self.menu, menu_data.get('items'))
            self.menu.add_cascade(
                label=menu_data.get('title'),
                menu=widget
            )
            # Todo add_radiobutton

        self.parent.config(menu=self.menu)

    def _create_menu(self, menu, items):
        widget = tk.Menu(menu, tearoff=0)
        for item in items:
            if item.get('title') == 'sep':
                widget.add_separator()
            else:
                widget.add_command(**item)
        return widget

    def load_view(self, name):
        view = View(self, name)
        self.views.append(view)
        self.current_view = view

    # Menu events

    def on_quit(self, *args):
        self.quit()

    def on_save_view(self, *args):
        self.current_view.on_save()

    def on_postscript_view(self, *args):
        self.current_view.on_postscript()

    def on_create_label(self, *args):
        self.current_view.on_create_label()

    def on_create_table(self, *args):
        self.current_view.on_create_table()

