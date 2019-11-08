import inspect as sp
import pathlib as pt

import baostock as bs
import pandas as pd

from tkinter import Tk
from tkinter import ttk
from tkinter import Toplevel

import matplotlib as mp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


###############
# CONFIG PART #
###############

# path to persist data
floc = "data/"
floc_data = floc + "vals/"
floc_vars = floc + "vars.csv"
floc_funcs = floc + "funcs.csv"

# globals
var_list = None
var_heads = ["name", "query", "args"]
func_list = None
func_heads = ["name", "value"]
data_list = None


#######################
# COMPUTATIAONAL PART #
#######################

# variable substitution and eqation evaluation
def sub(eqa, var_df):

    # helper method for function sub
    # TODO: Add zero division detection and handling
    def sub_helper(map, eqa):
        return eval(eqa, map)

    return var_df.apply(sub_helper, axis=1, args=eqa)

# validate equation
def eqation_validate(eqa, vars):
    try:
        eval(eqa, dict(vars, [1]*len(vars)))
    except ZeroDivisionError:
        pass
    except:
        return False
    return True


#################
# DATA I/O PART #
#################

# initialize data
def data_load():
    pt.Path(floc).mkdir(exist_ok=True)
    pt.Path(floc_data).mkdir(exist_ok=True)
    global var_list
    global func_list
    global data_list
    var_list = read_persist(floc_vars, var_heads)
    func_list = read_persist(floc_funcs, func_heads)
    data_list = get_all_func()
    return (var_list, func_list)

# add new variable
def add_var(name, func, args):
    var_list.append(pd.DataFrame([name, str(func), str(args)],
                        columns=var_heads), ignore_index=True)

# add new function
def add_func(name, func):
    func_list.append(pd.DataFrame([name, str(func)],
                        columns=func_heads), ignore_index=True)

# write to disk
def write_all():
    write_var()
    write_func()

# write variables
def write_var():
    var_list.to_csv(floc_vars)

# write a specific var value
def write_var_df(var_name, df):
    df.to_csv(floc_data+var_name+".csv")

# read a group of var value
def read_Vars(var_names):
    results=[]
    
    def helper(map):
        if map['name'] in var_names:
            p = floc_data+map['name']+".csv"
            if pt.Path(p).is_file():
                results.append(pd.read_csv(p))
            else:
                df = get_stock_data(map['func'], eval(map['args']))
                df.to_csv(p)
                results.append(df)
        return map
    
    var_list.apply(helper, axis=1)
    return results

# write function
def write_func():
    func_list.to_csv(floc_funcs)

# create if not exist
def read_persist(file_loc, heads):
    if pt.Path(file_loc).is_file():
        result = pd.read_csv(file_loc)
    else:
        result = pd.DataFrame(columns=heads)
        result.to_csv(file_loc, index=False)
    return result

# retrieve data from baostock
def get_stock_data(func, args):
    return func(*args)

# return a dict of <function name, function>
def get_all_func():
    result = dict(sp.getmembers(bs, sp.isfunction))
    if 'login' in result:
        del result['login']
    if 'logout' in result:
        del result['logout']
    return result

# return a tuple of arg names and kwarg names (args, kwargs)
def get_all_args(func):
    return sp.signature(func).parameters

############
# GUI PART #
############

# initialize gui
def gui_load():
    gui = Tk()
    nt = ttk.Notebook(gui)
    nt.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)
    vf = var_frame(nt)
    nt.add(vf, text="variables")
    ff = func_frame(nt)
    nt.add(ff, text="functions")
    return gui

# variable window
def var_frame(master):
    global var_list
    global data_list
    f = ttk.Frame(master)
    lf = list_frame(f, var_list)
    lf.pack()
    cb = ttk.Combobox(f, values=data_list.keys())
    cb.pack()
    b = ttk.Button(f, text="add", command=lambda: pop_add(data_list[cb.get()]))
    b.pack()
    return f

# function window
def func_frame(master):
    global func_list
    f = ttk.Frame(master)
    lf = list_frame(f, func_list)
    lf.pack()
    b = ttk.Button(f, text="add", command=lambda: pop_add(["name", "value"]))
    b.pack()
    return f

# universal list frame
def list_frame(master, df):
    tree = ttk.Treeview(master, columns=tuple(df.columns.values), show='headings')
    for col in df.columns.values:
        tree.column(col, width=100)
        tree.heading(col, text=col)
    for row in range(len(df)):
        tree.insert('', row, values=(df.iloc[row].tolist))
    return tree

# calls a popup window for a plot
def pop_graph(name, df):
    pop = Toplevel()
    lf = ttk.LabelFrame(pop, text=name)
    lf.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    df.reset_index().plot(x='index', y=df.columns.values, ax=ax)

    canvas = FigureCanvasTkAgg(fig, master=lf)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

# calls a popup window for adding var/func
def pop_add(val):
    func = None
    if callable(val):
        func = val
        args = get_all_args(func)
    else:
        args = val

    pop = Toplevel()
    f = ttk.Frame(pop)
    f.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)
    entry_list = []
    args.insert(0, 'name')
    for arg in args:
        l = ttk.Label(f, text=arg)
        l.pack()
        e = ttk.Entry(f)
        e.pack()
        entry_list.append(e)
    
    def submit():
        if func:
            add_var(entry_list[0].get(), func, [entry.get() for entry in entry_list[1:]])
        else:
            add_func(entry_list[0].get(), entry_list[1].get())
        # TODO: checking if add var/func arguments valid
        pop.quit

    b = ttk.Button(f, text="submit", command=submit)
    b.pack()


###############
# DRIVER PART #
###############

# Driver code
if __name__ == "__main__":
    data_load()
    gui = gui_load()
    gui.mainloop()
