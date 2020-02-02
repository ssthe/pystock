import inspect as sp
import json
import pathlib as pt

import baostock as bs
import pandas as pd

import config


class data():

    # constructor
    # read all the data if exist
    def __init__(self):
        pt.Path(config.floc).mkdir(exist_ok=True)
        pt.Path(config.floc_data).mkdir(exist_ok=True)
        self.usr_vars = self.read_persist(config.floc_vars)
        self.usr_exps = self.read_persist(config.floc_exps)
        self.db_funcs = self.get_all_func()
        self.db_datas = self.get_all_data()

    # json helper
    def name_to_floc(self, name):
        return config.floc_data + name + ".json"

    # write to disk
    def write_all(self):
        self.write_var()
        self.write_exp()

    # write variables
    def write_var(self):
        with open (config.floc_vars, 'w+') as f:
            json.dump(self.usr_vars, f)

    # write expression
    def write_exp(self):
        with open (config.floc_exps, 'w+') as f:
            json.dump(self.usr_exps, f)
    
    # write data
    def write_data(self, name, data):
        data.to_json(self.name_to_floc(name))

    # create persist file if not exist
    def read_persist(self, file_loc):
        if pt.Path(file_loc).is_file():
            with open (file_loc, 'r') as f:
                result = json.load(f)
                #for key in result.keys():
                #    if isinstance(result[key], list) and len(result[key]) == 1:
                #        result[key] = result[key][0]
        else:
            result = {}
        return result

    # save data
    def save_data(self, name):
        df = self.get_stock_data(self.db_funcs[self.usr_vars[name][0]], self.usr_vars[name][1:])
        self.write_data(name, df)
        self.db_datas[name] = df

    # retrieve data from baostock
    def get_stock_data(self, func, args):
        bs.login()
        rs = func(*args)
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        bs.logout()
        return result

    # return a dict of <function name, function>
    def get_all_func(self):
        # TODO: Still some functions not sutable for such treatment
        # need to specify column as some function returns a table
        result = dict(sp.getmembers(bs, sp.isfunction))
        if 'login' in result:
            del result['login']
        if 'logout' in result:
            del result['logout']
        return result

    # return a tuple of arg names and kwarg names (args, kwargs)
    def get_all_args(self, func):
        return sp.signature(func).parameters

    # read all jsons infered by var list
    def get_all_data(self):
        result = {}
        # This part does not consider deleting none-working names
        for name in self.usr_vars.keys():
            f = self.name_to_floc(name)
            if pt.Path(f).is_file():
                result[name] = pd.read_json(f).sort_index()
        for name in self.usr_exps.keys():
            f = self.name_to_floc(name)
            if pt.Path(f).is_file():
                result[name] = pd.read_json(f).sort_index()
        return result

    # return true if the name provided is defined
    def has_key(self, name):
        return name in self.usr_exps or name in self.usr_vars

    # return true if the name provided has local data
    def has_data(self, name):
        return name in self.db_datas
