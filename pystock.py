import pandas as pd
import baostock as bs
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

# retrieve data from baostock
def get_stock_data(**kwargs):
	lg = bs.login()
	# 显示登陆返回信息
	print('login respond error_code:'+lg.error_code)
	print('login respond  error_msg:'+lg.error_msg)

	#### 获取历史K线数据 ####
	# 详细指标参数，参见“历史行情指标参数”章节
	rs = bs.query_history_k_data_plus("sh.600000",
		"date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
		start_date='2017-06-01', end_date='2017-12-31', 
		frequency="d", adjustflag="3") #frequency="d"取日k线，adjustflag="3"默认不复权
	print('query_history_k_data_plus respond error_code:'+rs.error_code)
	print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

	#### 打印结果集 ####
	data_list = []
	while (rs.error_code == '0') & rs.next():
		# 获取一条记录，将记录合并在一起
		data_list.append(rs.get_row_data())
	result = pd.DataFrame(data_list, columns=rs.fields)
	#### 结果集输出到csv文件 ####
	result.to_csv("D:/history_k_data.csv", encoding="gbk", index=False)
	print(result)

	#### 登出系统 ####
	bs.logout()


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
