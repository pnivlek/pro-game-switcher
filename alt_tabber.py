#!/usr/bin/env python3

import logging
import os
import sys
import tkinter as tk

import psutil

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    filename='/home/yack/doc/pyt/alt_tabber/pgs.log'
)

class ApplicationController(object):

    def __init__(self):
        self.thread_scheduler = BackgroundScheduler()

        # Load or set up the config.
        self.yaml_path = self._find_config_home()
        try:
            self.yaml_config = yaml.safe_load(open(self._find_config_home()))
            if self.yaml_config is None:
                logging.getLogger(__name__).warning("YAML found but empty, remaking.")
                self.yaml_config = []
            else:
                logging.getLogger(__name__).debug("YAML found and loaded.")
        except FileNotFoundError:
            logging.getLogger(__name__).warning("No YAML found. Making a new one.")
            open(self.yaml_path, 'a').close()
            self.yaml_config = []
        except yaml.YAMLError:
            logging.getLogger(__name__).warning("Something's wrong with the YAML... remaking.")
        for job in self.yaml_config:
            self.thread_scheduler.add_job(lambda: self._check_for_processes(list(job.keys())[0]),
                                          id=list(job.keys())[0], trigger=IntervalTrigger(minutes=list(job.values())[0]))
        logging.getLogger(__name__).debug("Initialized jobs.")

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

    def _save_config(self):
        with open(self.yaml_path, 'w') as yp:
            yaml.dump(self.yaml_config, yp)
        print("Saved config.")

    def _update_processes(self):
        self.current_processes.delete(0,'end')
        try:
            proc_to_add = [str(["{:<20}  {:<3}".format(p,i) for p,i in proc.items()]) for proc in self.yaml_config]
            for i,proc in enumerate(self.yaml_config):
                self.current_processes.insert(i, "{:<15} {:<3}".format(list(proc.keys())[0],list(proc.values())[0]))
        except AttributeError:
            raise
        self.current_processes.grid(row=3, column=0)
        

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
            self._save_config()

        self._update_processes()

    def _delete_proc_cursor(self, selected):
        procname = self.current_processes.get(selected[0])[:-3].strip()
        interval = int(self.current_processes.get(selected[0])[-3:])
        for i,x in enumerate(self.yaml_config):
            if procname == list(x.keys())[0] and interval == list(x.values())[0]:
                del self.yaml_config[i]
        self._save_config()

        self.thread_scheduler.remove_job(self.current_processes.get(selected[0])[:-3].strip())
        self.current_processes.delete(selected[0])
        self._update_processes()


    def _check_for_processes(self, procname):
        do_alt_tab = False
        for proc in psutil.process_iter():
            if proc.name() in procname:
                do_alt_tab = True
        if do_alt_tab:
            self.alt_tab()

    def alt_tab(self):
        if "mac" in sys.platform:
            pyautogui.hotkey('command', 'tab')
        else:
            pyautogui.hotkey('alt', 'tab')

    def _init_gui(self):
        oriR = 1
        oriC = 0

        # Create the root window
        root = tk.Tk()
        root.geometry("500x400")
        root.title("Pro Gamer Switcher")

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

        self.current_processes = tk.Listbox(root)
        try:
            proc_to_add = [str(["{:<20}  {:<3}".format(p,i) for p,i in proc.items()]) for proc in self.yaml_config]
            for i,proc in enumerate(self.yaml_config):
                self.current_processes.insert(i, "{:<15} {:<3}".format(list(proc.keys())[0],list(proc.values())[0]))
        except AttributeError:
            raise
        self.current_processes.grid(row=oriR+2, column=oriC)

        name_desc = tk.Label(root, text="Process:")
        name_desc.grid(row=oriR+1, column=oriC)
        name_entry = tk.Entry(root, width=10)
        name_entry.grid(row=oriR+1, column=oriC+1)
        interval_desc = tk.Label(root, text="Interval (min):")
        interval_desc.grid(row=oriR+1, column=oriC+5)
        interval_entry = tk.Entry(root, width=3)
        interval_entry.grid(row=oriR+1, column=oriC+6)

        add_btn = tk.Button(root, text="Add", command=lambda: self._add_proc(name_entry.get(),
                                                                       int(interval_entry.get())))
        add_btn.grid(row=oriR+1, column=oriC+7)
        del_btn = tk.Button(root, text="Delete", command=lambda:
                            self._delete_proc_cursor(self.current_processes.curselection()))
        del_btn.grid(row=oriR+2, column=oriC+7)

        root.mainloop()

app = ApplicationController()
app.thread_scheduler.start()
app._init_gui()
