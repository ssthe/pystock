import inspect as sp
import pathlib as pt
import json

import baostock as bs
import pandas as pd

from tkinter import Tk
from tkinter import ttk
from tkinter import Toplevel
from tkinter import messagebox

import matplotlib as mp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


###############
# CONFIG PART #
###############

# path to persist data
floc = "data/"
floc_vars = floc + "vars.json"
floc_funcs = floc + "funcs.json"
floc_data = floc + "vals/"

# globals
# list of user variables
var_list = None
# list of user functions
func_list = None
# list of data getting fucntions
data_list = None
# list of loaded data in json
json_list = None


#######################
# COMPUTATIAONAL PART #
#######################

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
    global json_list
    var_list = read_persist(floc_vars)
    func_list = read_persist(floc_funcs)
    data_list = get_all_func()
    json_list = get_all_json()
    #return (var_list, func_list)

# write to disk
def write_all():
    write_var()
    write_func()

# write variables
def write_var():
    with open (floc_vars, 'w') as fv:
        json.dump(var_list, fv)

# write function
def write_func():
    with open (floc_funcs, 'w') as ff:
        json.dump(func_list, ff)

# create if not exist
def read_persist(file_loc):
    if pt.Path(file_loc).is_file():
        with open (file_loc, 'r') as fl:
            result = json.load(fl)
            for key in result.keys():
                if isinstance(result[key], list) and len(result[key]) == 1:
                    result[key] = result[key][0]
    else:
        result = {}
    return result

# retrieve data from baostock
def get_stock_data(func, args):
    bs.login()
    rs = func(*args)
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    #print(result)
    bs.logout()
    return result

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

# read all jsons infered by var list
def get_all_json():
    global var_list
    result = {}
    for name in var_list.keys():
        if pt.Path(floc_data+name+".json").is_file():
            result[name] = pd.read_json(floc_data+name+".json")
    return result

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
    bsave = ttk.Button(gui, text="save", command=write_all)
    bsave.grid(row=1, column=0)

    gui.rowconfigure(0, weight=1)
    gui.columnconfigure(0, weight=1)

    return gui

# variable window
def var_frame(master):
    global var_list
    global data_list
    global json_list
    f = ttk.Frame(master)
    lf = list_frame(f, ['name', 'val'], [[name, var_list[name]]for name in var_list.keys()])
    lf.grid(row=0, column=0, columnspan=2, sticky='nwes')
    cb = ttk.Combobox(f, values=list(data_list.keys()))
    cb.grid(row=1, column=0)
    b = ttk.Button(f, text="add", command=lambda: pop_add(data_list[cb.get()], lf))
    b.grid(row=1, column=1)
    
    def delete():
        del var_list[lf.item(lf.focus())['values'][0]]
        lf.delete(lf.focus())
    d = ttk.Button(f, text="delete", command=delete)
    d.grid(row=2, column=0)

    def get_data():
        name = lf.item(lf.focus())['values'][0]
        df = get_stock_data(data_list[var_list[name][0]], var_list[name][1:])
        df.to_json(floc_data+name+".json")
        json_list[name] = df
    c = ttk.Button(f, text="get data!", command=get_data)
    c.grid(row=2, column=1)

    for i in range(2):
        f.columnconfigure(i, weight=1)
    f.rowconfigure(0, weight=1)

    return f

# function window
def func_frame(master):
    global func_list
    global json_list
    f = ttk.Frame(master)
    lf = list_frame(f, ['name', 'val'], [[name, func_list[name]]for name in func_list.keys()])
    lf.grid(row=0, column=0, columnspan=3, sticky='nwes')
    b = ttk.Button(f, text="add", command=lambda: pop_add(['name', 'val'], lf))
    b.grid(row=1, column=0)

    def delete():
        del func_list[lf.item(lf.focus())['values'][0]]
        lf.delete(lf.focus())
    d = ttk.Button(f, text="delete", command=delete)
    d.grid(row=1, column=1)

    def valuate():
        values = lf.item(lf.focus())['values']
        result = eval(values[1], {}, json_list)
        pop_result(values[0], result)
    ev = ttk.Button(f, text="eval", command=valuate)
    ev.grid(row=1, column=2)

    for i in range(3):
        f.columnconfigure(i, weight=1)
    f.rowconfigure(0, weight=1)

    return f

# universal list frame
def list_frame(master, heads, lists):
    tree = ttk.Treeview(master, columns=heads, show='headings')
    for h in heads:
        tree.column(h, width=100)
        tree.heading(h, text=h)
    for l in range(len(lists)):
        tree.insert('', l, values=lists[l])
    return tree

def pop_result(name, result):
    pop = Toplevel()
    if isinstance(result, pd.DataFrame):
        lf = list_frame(pop, result.columns.values.tolist(), result.values.tolist())
    elif isinstance(result, list):
        lf = list_frame(pop, ['list'], result)
        result = pd.DataFrame(result)
    else:
        result = [result]
        lf = list_frame(pop, ['val'], result)
        result = pd.DataFrame(result)
    lf.grid(row=0, column=0, sticky='nwes')
    g = ttk.Button(pop, text="graph it!", command=lambda: pop_graph(name, result))
    g.grid(row=1, column=0)

    pop.columnconfigure(0, weight=1)
    pop.rowconfigure(0, weight=1)

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
def pop_add(val, tree):
    data = None
    if callable(val):
        data = val
        args = list(get_all_args(data))
        args.insert(0, 'name')
    else:
        args = list(val)

    pop = Toplevel()
    f = ttk.Frame(pop)
    f.grid(row=0, column=0, sticky='nwes', padx=3, pady=3)
    entry_list = []
    for arg in args:
        l = ttk.Label(f, text=arg)
        l.pack()
        e = ttk.Entry(f)
        e.pack()
        entry_list.append(e)
    
    def submit():
        result = [entry.get() for entry in entry_list]
        if result[0] in var_list or result[0] in func_list:
            messagebox.showinfo(title="Message", message="Failed to submit, name already exist!")
            return
        if data:
            var_list[result[0]] = [data.__name__] + result[1:]
            tree.insert('', len(var_list), values=[result[0], [data.__name__]+result[1:]])
        else:
            func_list[result[0]] = result[1:]
            tree.insert('', len(func_list), values=result)
        # TODO: checking if add var/func arguments valid
        pop.destroy()

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
