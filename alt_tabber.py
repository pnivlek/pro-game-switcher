#!/usr/bin/env python3

import tkinter as tk
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class ApplicationController(object):

    def __init__(self):
        self.thread_scheduler = BackgroundScheduler()

        # Load or set up the config.
        self.yaml_path = self.find_config_home
        try:
            self.yaml_config = yaml.safe_load(open(self._find_config_home))
        except yaml.YAMLError:
            os.mknod(self.yaml_path)

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
            self.thread_scheduler.add_job(self._check_for_processes, id=procname, trigger=IntervalTrigger(minutes=interval))
            self.yaml_config.append({procname: interval})
            with open(self.yaml_path, 'w') as yp:
                yaml.dump(self.yaml_config, yp)

    def _check_for_processes(self, procname):
        do_alt_tab = False
        for proc in psutil.process_iter():
            if proc.name() in procname:
                do_alt_tab = True
        if do_alt_tab:
            self.alt_tab()

    def alt_tab():
        pyautogui.hotkey('alt', 'tab')
