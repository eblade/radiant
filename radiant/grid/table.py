#!/usr/bin/env python3

from ..tk import tk, ttk, Dialog
from ._item import Item, TkProperty, MethodProperty


class Table(Item):
    """
    A table that allows displaying and editing of data.
    """
    title = TkProperty(
        "Table", "title_label", "text", None)
    title_font = TkProperty(
        "Table", "title_label", "font", ("Helvetica", 8))
    title_color = TkProperty(
        "Table", "title_label", "fill", "black")
    source = MethodProperty(
        "Table", "source", None)

    def set_source(self, source):
        self.source.forget(self)
        source.listen(self, self.on_data_change)

    def create(self, name, position):
        self.name = name
        x, y = self.position = position

        self.activate_options()

        title_options = {"anchor": tk.NW, "tags": (self._assembly_tag)}
        title_options['text'] = name.upper()
        title_options.update(self.tkoptions("title_label"))
        title_position = (x, y - self.title_font[1] - 2)

        self.title_label = self._view.canvas.create_text(
            title_position, **title_options
        )

        self._created = True
