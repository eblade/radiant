#!/usr/bin/env python3

from ..tk import tk, ttk, Dialog
from ._item import Item, TkProperty, MethodProperty


class Label(Item):
    """
    Simple text display with a title.
    """
    font = TkProperty(
        "Label", "value_label", "font", ("Helvetica", 12))
    color = TkProperty(
        "Label", "value_label", "fill", "black")
    text = MethodProperty(
        "Label", "text", None)
    title = TkProperty(
        "Label", "title_label", "text", None)
    title_font = TkProperty(
        "Label", "title_label", "font", ("Helvetica", 8))
    title_color = TkProperty(
        "Label", "title_label", "fill", "black")
    width = TkProperty(
        "Label", "value_label", "width", 100)
    editable = MethodProperty(
        "Label", "editable", False)
    show_title = MethodProperty(
        "Label", "show_title", True)
    variable = MethodProperty(
        "Label", "variable", None)
    
    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)

    def set_text(self, value):
        if self.variable is not None:
            self._view.scope.update(self.variable, value)
        else:
            self._itemconfig("value_label", text=value)

    def set_editable(self, value):
        activefill = "blue" if value else None
        self._itemconfig("value_label", activefill=activefill)

    def set_variable(self, variable):
        self._view.scope.define(variable)
        self._view.scope.listen(self, "text", variable, self.on_text_change)
        self.on_text_change(self._view.scope.get(variable))

    def set_show_title(self, value):
        state = tk.NORMAL if value else tk.HIDDEN
        self._itemconfig("title_label", state=state)

    def create(self, name, position):
        self.name = name
        x, y = self.position = position

        common_options = {
            "anchor": tk.NW,
            "tags": (self._assembly_tag),
        }

        self.activate_options()

        title_options = dict(common_options)
        title_options['text'] = name.upper()
        title_options.update(self.tkoptions("title_label"))
        title_position = (x, y - self.title_font[1] - 2)

        value_options = dict(common_options)
        value_options['text'] = '???'
        value_options.update(self.tkoptions("value_label"))
        value_position = position

        self.title_label = self._view.canvas.create_text(
            title_position, **title_options
        )
        self.value_label = self._view.canvas.create_text(
            value_position, **value_options
        )

        self._created = True

    def on_edit(self, *args):
        if self.editable:
            d = Dialog(self._view, self.name, value=self.text,
                       focus=self._view.canvas)
            if not d.cancelled:
                self.text = d.value

    def on_text_change(self, value):
        self._properties["text"] = value
        self._itemconfig("value_label", text=value)
