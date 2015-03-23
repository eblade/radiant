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
            server="localhost:8080",
            token="ABCDE",
            workspace="test",
        )
        
        # Set up Views
        self.views = []
        self.current_view = None
        self.create_view("View")

        self.parent.protocol('WM_DELETE_WINDOW', self.quit)

    def create_menu(self, *menus):
        self.menu=ttk.Menu(self.parent)
        
        for menu_data in menus:
            widget = self._create_menu(self.menu, menu_data.get('items'))
            self.menu.add_cascade(
                label=menu_data.get('title'),
                menu=widget
            )
            # Todo add_radiobutton

        self.parent.config(menu=self.menu)

    def _create_menu(self, menu, items):
        widget = ttk.Menu(menu, tearoff=0)
        for item in items:
            if item.get('title') == 'sep':
                var.add_separator()
            else:
                command=item.get('cmd')
                var.add_command(label=item.get('title'), command=command)
        return widget

    def create_view(self, title):
        view = View(self, title)
        self.views.append(view)
        self.current_view = view
