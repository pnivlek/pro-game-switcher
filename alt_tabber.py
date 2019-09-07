#!/usr/bin/env python3

import os
import sys
import tkinter as tk
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class ApplicationController(object):

    def __init__(self):
        self.thread_scheduler = BackgroundScheduler()

        # Load or set up the config.
        self.yaml_path = self._find_config_home()
        try:
            self.yaml_config = yaml.safe_load(open(self._find_config_home()))
            if self.yaml_config is None:
                self.yaml_config = []
        except FileNotFoundError:
            os.mknod(self.yaml_path)
            self.yaml_config = []
        except yaml.YAMLError:
            print("Something's wrong with the YAML... remaking.")

    def _find_config_home(self):
        platform = sys.platform
        if 'linux' in platform:
            return os.path.expanduser('~/.local/share/tabber.cfg')
        elif 'win32' in platform:
            return os.path.expanduser('~/AppData/Roaming/tabber.cfg')
        elif 'mac' in platform:
            return os.path.expanduser('~/Library/Application Support/tabber.cfg')
        else:
            print("Unknown OS. Only Windows, Mac, and Linux are supported.")
            return None

    def _add_proc(self, procname, interval):
        # IDs for the current jobs are equal to the procname
        if procname in [j.id for j in self.thread_scheduler.get_jobs()]:
            # it already exists, modify it
            self.thread_scheduler.modify_job(job_id=procname, trigger=IntervalTrigger(minutes=interval))
            # go through the list of current procname/interval k/v's and edit the combo
            for i, proc in enumerate(self.yaml_config):
                if proc == procname:
                    self.yaml_config[i][procname] = interval
        else:
            self.thread_scheduler.add_job(lambda: self._check_for_processes(procname), id=procname, trigger=IntervalTrigger(minutes=interval))
            self.yaml_config.append({procname: interval})
            with open(self.yaml_path, 'w') as yp:
                yaml.dump(self.yaml_config, yp)
            print("Saved config.")

    def _delete_proc(self, selected):
        for i,procname in enumerate(self.yaml_config):
            if selected[i] == 1:
                self.thread_scheduler.remove_job(procname)


    def _check_for_processes(self, procname):
        do_alt_tab = False
        for proc in psutil.process_iter():
            if proc.name() in procname:
                do_alt_tab = True
        if do_alt_tab:
            self.alt_tab()

    def alt_tab(self):
        pyautogui.hotkey('alt', 'tab')

    def _init_gui(self):
        oriR = 1
        oriC = 0

        # Create the root window
        root = tk.Tk()
        root.geometry("1000x800")
        root.title("Alt Tab")

        menu = tk.Menu(root)
        root.config(menu = menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New')
        filemenu.add_command(label='Open...')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=root.quit)
        helpmenu = tk.Menu(menu)
        menu.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='About')

        current_processes = tk.Listbox(root)
        try:
            proc_to_add = [str(["{:<20}  {:<3}".format(p,i) for p,i in proc.items()]) for proc in self.yaml_config]
            for i,proc in enumerate(self.yaml_config):
                current_processes.insert(i, "{:<15} {:<3}".format(list(proc.keys())[0],list(proc.values())[0]))
        except AttributeError:
            raise
        current_processes.grid(row=oriR+2, column=oriC)

        add_label = tk.Label(root, text="Add process")
        add_label.grid(row=oriR, column=oriC)
        name_desc = tk.Label(root, text="Process name:")
        name_desc.grid(row=oriR+1, column=oriC)
        name_entry = tk.Entry(root)
        name_entry.grid(row=oriR+1, column=oriC+1)
        interval_desc = tk.Label(root, text="Interval time:")
        interval_desc.grid(row=oriR+1, column=oriC+4)
        interval_entry = tk.Entry(root)
        interval_entry.grid(row=oriR+1, column=oriC+5)

        add_btn = tk.Button(root, text="Add", command=lambda: self._add_proc(name_entry.get(),
                                                                       int(interval_entry.get())))
        add_btn.grid(row=oriR+1, column=oriC+7)
        del_btn = tk.Button(root, text="Delete", command=lambda:
                            self._delete_proc_cursor(current_processes.curselection()))
        del_btn.grid(row=oriR+2, column=oriC+7)

        root.mainloop()

app = ApplicationController()
app._init_gui()
