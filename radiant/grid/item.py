#!/usr/bin/env python3

from .label import Label
from .table import Table


def ItemType(item_type):
    if item_type == "Label":
        return Label
    elif item_type == "Table":
        return Table
    else:
        raise TypeError("No such item type " + item_type)
