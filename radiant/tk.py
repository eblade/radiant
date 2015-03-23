#!/usr/bin/env python3

try:
    # Python 3
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    # Python 2
    import Tkinter as tk
    import ttk


import os

class Dialog(tk.Toplevel):

    def __init__(self, parent, title=None, value=None, focus=None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.focus_after = focus or parent

        self.result = None
        self.cancelled = True
        self.value = value

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method could be overridden
        
        
        tk.Label(master, text="Value").grid(row=0)
        self.entry = tk.Entry(master)
        if self.value:
            self.entry.insert(0, self.value)
        self.entry.grid(row=0, column=1)

        return self.entry
        

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancelled = False
        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.focus_after.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        return 1 # override

    def apply(self):
        self.value = self.entry.get()

