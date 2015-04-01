#!/usr/bin/env python3

from ..tk import tk, ttk


class TkProperty(object):
    _defaults = {}

    def __init__(self, klass, name, item, tkoption, default=None):
        self.k = klass
        self.name = name
        self.item = item
        self.tkoption = tkoption
        self.default = default

        if default is None:
            return
        
        if not self.k in self._defaults.keys():
            d = {}
            self._defaults[self.k] = d
        else:
            d = self._defaults[self.k]

        if not item in d.keys():
            dd = {}
            d[item] = dd
        else:
            dd = d[item]

        dd[tkoption] = default
        
    def __get__(self, obj, objtype):
        return obj._tkdict.get(self.item, {}).get(self.tkoption, self.default)

    def __set__(self, obj, value):
        obj._properties[self.name] = value

        if not self.item in obj._tkdict.keys():
            d = {}
            obj._tkdict[self.item] = d
        else:
            d = obj._tkdict[self.item]
        
        d[self.tkoption] = value

        if obj._created:
            tkindex = getattr(obj, self.item)
            obj._view.canvas.itemconfig(tkindex, **{self.tkoption: value})

    @classmethod
    def defaults(self, k):
        return dict(self._defaults.get(k, {}))


class MethodProperty(object):
    _defaults = {}

    def __init__(self, klass, name, default=None):
        self.k = klass
        self.name = name
        self.default = default

        if default is None:
            return

        if not self.k in self._defaults.keys():
            d = {}
            self._defaults[self.k] = d
        else:
            d = self._defaults[self.k]

        d[name] = default

    def __get__(self, obj, objtype):
        return obj._properties.get(self.name, self.default)

    def __set__(self, obj, value):
        method = getattr(obj, "set_" + self.name)
        method(value)
        obj._properties[self.name] = value
    
    @classmethod
    def defaults(self, k):
        return self._defaults.get(k, {})


class Item(object):
    """
    Generic selectable and movable complex tk Canvas item.
    """

    def __init__(self, view):
        self._view = view               # View object with the canvas
        self._name = None               # The unique instance name
        self._assembly_tag = None       # Constructed object-wide canvas tag
        self._position = None           # The current position
        self._handle_index = None       # Canvas index of the move handle
        self._handle_position = (0, 0)  # Position of the move handle
        self._tkdict = {}               # Tk options per sub-item
        self._properties = {}           # Other options
        self._created = False           # The create method should set this
                                        # to True

    @property
    def position(self):
        """
        Get the upper left corner of the object
        """
        if self._position is None:
            raise ValueError("Not initialized, position is None")
        elif len(self._position) == 2:
            return self._position
        elif len(self._position) == 4:
            return (
                min(self._position[0], self._position[2]),
                min(self._position[1], self._position[3])
            )
        else:
            raise ValueError("Bad position format "+str(self._position))

    def create(self, name):
        raise NotImplemented()

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def name(self):
        return self._name

    def config(self, **options):
        for k, v in options.items():
            setattr(self, k, v)

    def _itemconfig(self, name, **options):
        if not name in self._tkdict.keys():
            d = {}
            self._tkdict[name] = d
        else:
            d = self._tkdict[name]
        
        d.update(options)

        if self._created:
            tkindex = getattr(self, name)
            self._view.canvas.itemconfig(tkindex, **options)

    def delete(self):
        self._view.canvas.delete(self._assembly_name)

    @name.setter
    def name(self, name):
        self._name = name

        # Unbind old assembly events
        if self._assembly_tag is not None:
            self.unbind_select()

        # Update assembly tag and events
        self._assembly_tag = "_assembly_" + name
        self.bind_select()

    def bind_select(self):
        self._view.canvas.tag_bind(self._assembly_tag,
            "<Enter>", self.on_assembly_enter)

    def unbind_select(self):
        self._view.canvas.tag_unbind(self._assembly_tag,
            "<Enter>")

    def select(self):
        x, y = self.position

        # Create handle blupp
        self._handle_index = self._view.canvas.create_oval(
            *(self._handle_coords(x, y)),
            fill="blue", tags="_handle")

        # Register events for the handle blupp
        self._view.canvas.tag_bind(self._handle_index,
            "<ButtonPress-1>", self.on_handle_press)
        self._view.canvas.tag_bind(self._handle_index,
            "<B1-Motion>", self.on_handle_motion)
        
    def deselect(self):
        self._view.canvas.tag_unbind(self._handle_index,
            "<ButtonPress-1>")
        self._view.canvas.tag_unbind(self._handle_index,
            "<B1-Motion>")
        self._view.canvas.delete(self._handle_index)
        
    def _handle_coords(self, x, y):
        return x-8, y-5, x, y+3

    def _to_canvas_coords(self, x, y):
        return (
            self._view.canvas.canvasx(x),
            self._view.canvas.canvasy(y)
        )

    @property
    def is_selected(self):
        return self._handle_index is not None

    def on_assembly_enter(self, event):
        self._view.select(self._name)

    def on_handle_press(self, event):
        self._handle_position = self._to_canvas_coords(event.x, event.y)

    def on_handle_motion(self, event):
        x, y = self._view.snap(self._to_canvas_coords(event.x, event.y))
        delta = (x - self._position[0], y - self._position[1])
        self._position = (x, y)
        self._view.canvas.move(self._assembly_tag, *delta)
        self._view.canvas.coords(self._handle_index, self._handle_coords(x, y))
        self._handle_position = (x, y)

    def move(self, dx, dy):
        x, y = self._position
        x, y = self._view.snap((x + dx, y + dy))
        self._position = (x, y)
        self._view.canvas.move(self._assembly_tag, dx, dy)
        self._view.canvas.coords(self._handle_index, self._handle_coords(x, y))

    def on_edit(self, *args):
        pass

    def on_edit_text(self, *args):
        pass

    def activate_options(self):
        tkoptions = dict(TkProperty.defaults(self.__class__.__name__))
        properties = dict(MethodProperty.defaults(self.__class__.__name__))
        properties.update(self._properties)
        for k, v in properties.items():
            setattr(self, k, v)
        tkoptions.update(self._tkdict)
        self._tkdict = tkoptions
    
    def tkoptions(self, name):
        return dict(self._tkdict.get(name, {}))
        
    def to_dict(self):
        return {
            "data-type": "grid/item/entry",
            "item-type": self.__class__.__name__,
            "name": self._name,
            "properties": self._properties,
            "position": self._position,
        }
