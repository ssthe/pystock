import pandas as pd
import tkinter as tk

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
    pass

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
