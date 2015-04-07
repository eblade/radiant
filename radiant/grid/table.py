#!/usr/bin/env python3

from ..tk import tk, ttk, Dialog
from ._item import Item, TkProperty, MethodProperty


class Table(Item):
    """
    A table that allows displaying and editing of data.
    """
    font = TkProperty(
        "Table", "font", "value_label", "font", ("Helvetica", 12))
    color = TkProperty(
        "Table", "color", "value_label", "fill", "black")
    title = TkProperty(
        "Table", "title", "title_label", "text", None)
    title_font = TkProperty(
        "Table", "title_font", "title_label", "font", ("Helvetica", 8))
    title_color = TkProperty(
        "Table", "title_color", "title_label", "fill", "black")
    source = MethodProperty(
        "Table", "source", None)
    editable = MethodProperty(
        "Table", "editable", True)
    show_title = MethodProperty(
        "Table", "show_title", True)
    source = MethodProperty(
        "Table", "source", None, empty=False)

    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
        self.document = None  # Binding to a document or meta-document

    def set_editable(self, value):
        pass

    def set_source(self, source):
        if self.document is not None:
            self.document.forget(self)
        self.document = self._view.workspace.get_document_binding(source)
        self.document.listen(self, self.on_data_change)

    def get_source_names(self):
        sources = self._view.workspace.adapter.enum_documents()
        return sources.entries

    def set_show_title(self, value):
        state = tk.NORMAL if value else tk.HIDDEN
        self._itemconfig("title_label", state=state)

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

    def on_edit(self, *args):
        if self.editable:
            d = TableDialog(self._view, self.name, value=self,
                            focus=self._view.canvas)
            if not d.cancelled:
                pass


class TableDialog(Dialog):
    # override
    def body(self, master):
        row = 0
        # Name
        tk.Label(master, text="Name").grid(row=row)
        self.name_entry = tk.Entry(master)
        self.name_entry.insert(0, self.value.name)
        self.name_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Source
        tk.Label(master, text="Source").grid(row=row)
        self.source_name = tk.StringVar()
        self.source_name.set(self.value.source or "[no document]")
        tk.OptionMenu(master, self.source_name,
            "[no document]", 
            *(self.value.get_source_names())
        ).grid(row=row, column=1, sticky=tk.W)
        row += 1

        self.create_source_button = tk.Button(master, text="Create Document...")
        self.create_source_button.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        self.columns_button = tk.Button(master, text="Edit Columns...")
        self.columns_button.grid(row=row, column=1, sticky=tk.W)
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
        self.title_entry.insert(1, self.value.title or self.value.name.upper())
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
        source = self.source_name.get()
        if source == "[no document]":
            source = None
        editable = True if self.editable_check.get() else False
        show_title = True if self.title_check.get() else False
        title = self.title_entry.get()
        title_font = (self.title_font_name.get(), int(self.title_font_size.get()))
        title_color = self.title_color_entry.get()
        font = (self.text_font_name.get(), int(self.text_font_size.get())) 
        color = self.text_color_entry.get()

        if name != self.value.name:
            pass  # for now
        if source != self.value.source:
            self.value.source = source
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
