from re import split
from tkinter import Tk, Toplevel, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import data
from lang import lang


def main_window(master, data):
    notebook = ttk.Notebook(master)
    notebook.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)
    var_frame = Var_frame(data, master=notebook)
    notebook.add(var_frame, text=lang.variables)
    exps_frame = Exps_frame(data, master=notebook)
    notebook.add(exps_frame, text=lang.functions)
    save_button = ttk.Button(master, text=lang.save, command=data.write_all)
    save_button.grid(row=1, column=0)

    master.rowconfigure(0, weight=1)
    master.columnconfigure(0, weight=1)

    return master


# construct a table from treeview widget
class Table_tree(ttk.Treeview):
    def __init__(self, heads, lists, master=None):
        super().__init__(master=master, columns=heads, show='headings')
        for h in heads:
            self.column(h, width=100)
            self.heading(h, text=h)
        for l in range(len(lists)):
            self.insert('', l, values=lists[l])


# basic table frame structure
class List_frame(ttk.Frame):
    def __init__(self, data, data_dict, master=None, **kw):
        super().__init__(master=master, **kw)
        # data reference
        self.data = data
        # table frame
        self.list_frame = Table_tree(('name', 'val'), list(data_dict.items()), master=self)
        self.list_frame.grid(row=0, column=0, columnspan=3, sticky='nwes')
    
    # helper for getting name of focus on list frame
    def focus_name(self):
        return self.list_frame.item(self.list_frame.focus())['values'][0]


# variable window
class Var_frame(List_frame):
    # constructor
    def __init__(self, data, master=None, **kw):
        super().__init__(data, data.usr_vars, master=master, **kw)
        # combobox for function selection
        self.combobox = ttk.Combobox(self, values=list(data.db_funcs.keys()))
        self.combobox.grid(row=1, column=0, columnspan=2)
        # add button
        self.add_button = ttk.Button(self, text=lang.add, command=self.pop_add)
        self.add_button.grid(row=1, column=2)
        # delete button
        self.delete_button = ttk.Button(self, text=lang.delete, command=self.delete)
        self.delete_button.grid(row=2, column=0)
        # show data button
        self.show_button = ttk.Button(self, text=lang.show_data, command=self.pop_data)
        self.show_button.grid(row=2, column=1)
        # get data button
        self.get_button = ttk.Button(self, text=lang.get_data, command=self.get_data)
        self.get_button.grid(row=2, column=2)
        # set expanding weight
        for i in range(3):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)

    # command for get button
    def get_data(self):
        self.data.save_data(self.focus_name())
    
    # command for show button
    def pop_data(self):
        name = self.focus_name()
        if self.data.has_data(name):
            Result_pop(self.data.db_datas[self.focus_name()], master=self)
        else:
            messagebox.showinfo(title=lang.warnning, text=lang.msg_get_data_first)

    # command for add button
    def pop_add(self):
        func = self.data.db_funcs[self.combobox.get()]
        args = list(self.data.get_all_args(func))
        args.insert(0, 'name')
        def submit(results):
            self.data.usr_vars[results[0]] = [func.__name__] + results[1:]
            self.list_frame.insert('', len(self.data.usr_vars), values=[results[0], [func.__name__]+results[1:]])
        Add_pop(self.data, submit, args=args)
    
    # command for delete button
    def delete(self):
        del self.data.usr_vars[self.focus_name()]
        self.list_frame.delete(self.list_frame.focus())


# function window
class Exps_frame(List_frame):

    def __init__(self, data, master=None, **kw):
        super().__init__(data, data.usr_exps, master=master, **kw)
        # add_button
        self.add_button = ttk.Button(self, text=lang.add, command=self.pop_add)
        self.add_button.grid(row=1, column=0)
        # delete button
        self.delete_button = ttk.Button(self, text=lang.delete, command=self.delete)
        self.delete_button.grid(row=1, column=1)
        # evaluate button
        self.eval_button = ttk.Button(self, text=lang.valuate, command=self.valuate)
        self.eval_button.grid(row=1, column=2)

        for i in range(3):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)

    def parse_names(self, expression):
        results = split(r"[\+ \- \* \/ \. \( \)]", expression)
        return [r for r in results if not r.isdigit()]
    
    def valuate(self):
        exp = self.data.usr_exps[self.focus_name()]
        #var_names = self.parse_names(exp)
        result = eval(exp, {}, self.data.db_datas)
        Result_pop(result, master=self)

    def pop_add(self):
        args = ['name', 'val']
        def submit(results):
            self.data.usr_exps[results[0]] = results[1]
            self.list_frame.insert('', len(self.data.usr_exps), values=results)
        Add_pop(self.data, submit, args=args)

    def delete(self):
        del self.data.usr_exps[self.focus_name()]
        self.list_frame.delete(self.list_frame.focus())


# add window
class Add_pop(Toplevel):
    # constructor
    def __init__(self, data, submit, master=None, args=[], cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.data = data
        self.submit = submit
        # main frame
        self.frame = ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)
        # list of entries
        self.entry_list = []
        for arg in args:
            l = ttk.Label(self.frame, text=arg)
            l.pack()
            e = ttk.Entry(self.frame)
            e.pack()
            self.entry_list.append(e)

        self.submit_button = ttk.Button(self.frame, text=lang.submit, command=self.submit_command)
        self.submit_button.pack()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def get_results(self):
        return [entry.get() for entry in self.entry_list]

    def submit_command(self):
        results = self.get_results()
        if self.data.has_key(results[0]):
            messagebox.showinfo(title=lang.message, message=lang.msg_fail_submit)
        else:
            self.submit(results)
            self.destroy()
        '''
        if data:
            var_list[result[0]] = [data.__name__] + result[1:]
            tree.insert('', len(var_list), values=[result[0], [data.__name__]+result[1:]])
        else:
            func_list[result[0]] = result[1:]
            tree.insert('', len(func_list), values=result)
        # TODO: checking if add var/func arguments valid
        self.destroy()
        '''


# calls a popup window for result showing
class Result_pop(Toplevel):

    def __init__(self, result, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.result = result

        self.table = Table_tree(result.columns.values.tolist(), result.values.tolist(), master=self)
        self.table.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)

        self.graph_button = ttk.Button(self, text=lang.graph_it, command=self.pop_graph)
        self.graph_button.grid(row=1, column=0)

        for i in range(2):
            self.rowconfigure(i, weight=1)
        self.columnconfigure(0, weight=1)

    def pop_graph(self):
        Graph_pop(self.result, self)

    # calls a popup window for plot config
    def pop_graph_config(self, name, df):
        pass


# calls a popup window for a plot
class Graph_pop(Toplevel):
    def __init__(self, dataframe, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        rf = dataframe.reset_index()
        # rf.rename(columns={'index': xv}, inplace=True)
        rf.plot(x='index', y=dataframe.columns.values, ax=ax)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)
