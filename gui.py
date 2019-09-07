from tkinter import *

root = Tk()
root.geometry("500x400")
root.title("Alt Tab")

menu = Menu(root) 
root.config(menu = menu)
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu) 
filemenu.add_command(label='New')
filemenu.add_command(label='Open...') 
filemenu.add_separator() 
filemenu.add_command(label='Exit', command=root.quit) 
helpmenu = Menu(menu) 
menu.add_cascade(label='Help', menu=helpmenu) 
helpmenu.add_command(label='About') 



# Add process, Delete process, List of processes, Start, End


# List of processes
proc_list = ["", "a"]

# # print proc list
# def printProcL():
# 	for i in proc_list:
# 		print(i)
# 		print(type(i))

# # Append to proc_list
# def procLAppend(proc_entry_input):
# 	proc_list.append(proc_entry_input)
# 	printProcL()

# Title 
title = Label(root, text="Alt Tab")
title.grid(row=0, column=0)
      
# Add
oriR = 1
oriC = 0
def makeAdd(oriR, oriC):
	add_label = Label(root, text="Add process")
	add_label.grid(row=oriR, column=oriC)
	name_desc = Label(root, text="Process name:")
	name_desc.grid(row=oriR+1, column=oriC)
	proc_entry = Entry(root)
	proc_entry.grid(row=oriR+1, column=oriC+1)

	proc_entry_input = proc_entry.get()
	print(proc_entry_input)
	print(type(proc_entry_input))

	add_btn = Button(root, text="add", command=lambda root=root: proc_list.append(proc_entry_input))

	print(proc_list[0])
	print(proc_list[1])

	add_btn.grid(row=oriR+1, column=oriC+2)
	print(proc_entry_input)

makeAdd(1, 0)

root.mainloop()



