#!/usr/bin/env python3

from ..tk import tk, ttk, Dialog
from ._item import Item, TkProperty, MethodProperty


class Label(Item):
    """
    Simple text display with a title.
    """
    font = TkProperty(
        "Label", "font", "value_label", "font", ("Helvetica", 12))
    color = TkProperty(
        "Label", "color", "value_label", "fill", "black")
    text = MethodProperty(
        "Label", "text", None, unless="variable")
    title = TkProperty(
        "Label", "title", "title_label", "text", None)
    title_font = TkProperty(
        "Label", "title_font", "title_label", "font", ("Helvetica", 8))
    title_color = TkProperty(
        "Label", "title_color", "title_label", "fill", "black")
    width = TkProperty(
        "Label", "width", "value_label", "width", 100)
    editable = MethodProperty(
        "Label", "editable", True)
    show_title = MethodProperty(
        "Label", "show_title", False)
    variable = MethodProperty(
        "Label", "variable", None, removes="text", empty=False)
    
    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)

    def set_text(self, value):
        if self.variable is not None:
            self._view.workspace.scope.update(self.variable, value)
        else:
            self._itemconfig("value_label", text=value)

    def set_editable(self, value):
        activefill = "blue" if value else None
        self._itemconfig("value_label", activefill=activefill)

    def set_variable(self, variable):
        if variable:
            self._view.workspace.scope.define(variable)
            self._view.workspace.scope.listen(self, "text", variable, self.on_text_change)
            self.on_text_change(self._view.workspace.scope.get(variable))
        else:
            self._view.workspace.scope.nevermind(self, "text")
            return (None,)

    def by_variable(self):
        print("self.variable: " + str(self.variable))
        if self.variable:
            return self._view.workspace.scope.get(self.variable)

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

    def on_edit_text(self, *args):
        if self.editable:
            d = Dialog(self._view, self.name, value=self.text,
                       focus=self._view.canvas)
            if not d.cancelled:
                self.text = d.value
    
    def on_edit(self, *args):
        if self.editable:
            d = LabelDialog(self._view, self.name, value=self,
                            focus=self._view.canvas)
            if not d.cancelled:
                pass

    def on_text_change(self, value):
        self._properties["text"] = value
        self._itemconfig("value_label", text=value)


class LabelDialog(Dialog):
    # override
    def body(self, master):
        row = 0
        # Name
        tk.Label(master, text="Name").grid(row=row)
        self.name_entry = tk.Entry(master)
        self.name_entry.insert(0, self.value.name)
        self.name_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Variable
        tk.Label(master, text="Variable").grid(row=row)
        self.variable_entry = tk.Entry(master)
        self.variable_entry.insert(1, self.value.variable or '')
        self.variable_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Editable
        self.editable_check = tk.BooleanVar()
        self.editable_check.set(self.value.editable)
        tk.Checkbutton(
            master, text="Editable",
            onvalue=True, offvalue=False,
            variable=self.editable_check).grid(row=row, columnspan=2, sticky=tk.W)
        row += 1

        # Show Title
        self.title_check = tk.BooleanVar()
        self.title_check.set(self.value.show_title)
        tk.Checkbutton(
            master, text="Show Title",
            onvalue=True, offvalue=False,
            variable=self.title_check).grid(row=row, columnspan=2, sticky=tk.W)
        row += 1

        # Title
        tk.Label(master, text="Title").grid(row=row)
        self.title_entry = tk.Entry(master)
        self.title_entry.insert(1, self.value.title or '')
        self.title_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Title Font (name)
        tk.Label(master, text="Title Font").grid(row=row)
        self.title_font_name = tk.StringVar()
        self.title_font_name.set(self.value.title_font[0])
        tk.OptionMenu(master, self.title_font_name,
            "Helvetica", "Times", "Courier").grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Title Font (size)
        tk.Label(master, text="Title Font Size").grid(row=row)
        self.title_font_size = tk.Spinbox(master, from_=4, to=144)
        self.title_font_size.insert(1, self.value.title_font[1])
        self.title_font_size.delete(0, 1)
        self.title_font_size.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Title Color
        tk.Label(master, text="Title Color").grid(row=row)
        self.title_color_entry = tk.Entry(master)
        self.title_color_entry.insert(1, self.value.title_color)
        self.title_color_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Text
        tk.Label(master, text="Text").grid(row=row)
        self.text_entry = tk.Entry(master)
        self.text_entry.insert(1, self.value.text or '')
        self.text_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Font (name)
        tk.Label(master, text="Font").grid(row=row)
        self.text_font_name = tk.StringVar()
        self.text_font_name.set(self.value.font[0])
        tk.OptionMenu(master, self.text_font_name,
            "Helvetica", "Times", "Courier").grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Font (size)
        tk.Label(master, text="Font Size").grid(row=row)
        self.text_font_size = tk.Spinbox(master, from_=4, to=144)
        self.text_font_size.insert(1, self.value.font[1])
        self.text_font_size.delete(0, 1)
        self.text_font_size.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Text Color
        tk.Label(master, text="Title Color").grid(row=row)
        self.text_color_entry = tk.Entry(master)
        self.text_color_entry.insert(1, self.value.color)
        self.text_color_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        return self.name_entry

    def apply(self):
        name = self.name_entry.get()
        variable = self.variable_entry.get()
        editable = True if self.editable_check.get() else False
        show_title = True if self.title_check.get() else False
        title = self.title_entry.get()
        title_font = (self.title_font_name.get(), int(self.title_font_size.get()))
        title_color = self.title_color_entry.get()
        text = self.text_entry.get()
        font = (self.text_font_name.get(), int(self.text_font_size.get())) 
        color = self.text_color_entry.get()

        if name != self.value.name:
            pass  # for now
        if variable != self.value.variable:
            self.value.variable = variable
        elif text != self.value.text:
            self.value.text = text
        if editable != self.value.editable:
            self.value.editable = editable
        if show_title != self.value.show_title:
            self.value.show_title = show_title
        if title != self.value.title:
            self.value.title = title
        if title_font != self.value.title_font:
            self.value.title_font = title_font
        if title_color != self.value.title_color:
            self.value.title_color = title_color
        if font != self.value.font:
            self.value.font = font
        if color != self.value.color:
            self.value.color = color
