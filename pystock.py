import inspect as sp
import pathlib as pt
import tkinter as tk

import baostock as bs
import pandas as pd


###############
# CONFIG PART #
###############

# path to persist data
floc = "data/"
floc_vars = floc + "vars.csv"
floc_funcs = floc + "funcs.csv"

# globals
var_list = None
func_list = None


#######################
# COMPUTATIAONAL PART #
#######################

# helper method for function sub
# TODO: Add zero division detection and handling
def sub_eval(map, eqa):
	return eval(eqa, map)
	
# variable substitution and eqation evaluation
def sub(eqa, var_df):
	return var_df.apply(sub_eval, axis = 1, args = eqa)

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
	pt.Path(floc).mkdir(exist_ok = True)
	global var_list
	global func_list
	var_list = read_persist(floc_vars)
	func_list = read_persist(floc_funcs)

# add new variable
def add_var(name, func_and_args, csv_loc):
	var_list.append(pd.DataFrame([name, str(func_and_args), csv_loc], 
		columns=["name", "func-and-args", "csv-location"]), ignore_index=True)

# add new function
def add_func(name, func):
	func_list.append(pd.DataFrame([name, str(func)], columns=["name", "value"],
		), ignore_index=True)

# write to disk
def write_all():
	write_var()
	write_func()

# write variables
def write_var():
	var_list.to_csv(floc_vars)

# write function
def write_func():
	func_list.to_csv(floc_funcs)
	
# create if not exist
def read_persist(file_loc):
	if pt.Path(file_loc).is_file():
		result = pd.read_csv(file_loc)
	else:
		result = pd.DataFrame()
		result.to_csv(floc_vars)
	return result

# retrieve data from baostock
def get_stock_data(**kwargs):
	pass

# return a dict of <function name, function>
def get_all_func():
	result = dict(sp.getmembers(bs, sp.isfunction))
	if 'login' in result:
		del result['login']
	if 'logout' in result:
		del result['logout']
	return result


############
# GUI PART #
############

# initialize gui
def gui_load():
	gui = tk.Tk()
	return gui


###############
# DRIVER PART #
###############

# Driver code
if __name__ == "__main__":
	data_load()
	gui = gui_load()
	gui.mainloop()
