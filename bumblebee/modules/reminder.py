"""
    Reminder - a simple reminder widget for bumblebee
"""
import bumblebee.input
import bumblebee.output
import bumblebee.engine
import logging
# -----
def print(v):
    logging.debug(v)

from tkinter import Tk, Label, Button, Entry, StringVar
from datetime import datetime as dt, timedelta
from os import getenv, makedirs, listdir 
from random import random
path = getenv("HOME") + "/.reminder"
try:
    makedirs(path)
except Exception as e:
    logging.debug(e)

def rand_file():
    return path + '/r-' + '-'.join([ str( int (random() * 10000 ) ) for _ in range(3)])

_kinds = {
    "h": lambda n: timedelta(hours=n),
    "m": lambda n: timedelta(minutes=n),
    "s": lambda n: timedelta(seconds=n),
}

class ReminderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Reminder")

        self.label = Label(master, text="PyReminder")
        self.label.pack()

        self.start_button = Button(master, text="Start", command=self.start)
        self.start_button.pack()

        self.ev = StringVar()
        self.ev.trace_add("write", self.parse)
        
        self.entry = Entry(master,textvariable=self.ev)
        self.entry.pack()
        
        self.ev.set("10 m")

    def validateInput(self,value):
        if value is not None:
            self.entry.config(background="green")
        else:
            self.entry.config(background="red")
        self.target = value
        print(self.target)

    def parse(*args,**kwargs):
        self = args[0]
        try:
            text = self.ev.get().strip()
            t = text[0]
            if t == 'd' or t=='t':
                text = text[1:].strip()
                if t == 't':
                    text = str(dt.now())[0:10] + ' ' + text
                try:
                    dt.strptime(text, '%Y-%m-%d %H:%M:%S')
                except:
                    text += ":00"
                    try:
                        dt.strptime(text, '%Y-%m-%d %H:%M:%S')
                    except:
                        text += ":00"        
                target = dt.strptime(text, '%Y-%m-%d %H:%M:%S')
                if target < dt.now():
                    target += timedelta(days=1)                
                self.validateInput(target)
            else:
                text = text.split(' ')[0:2]
                num = float(text[0])
                kind = text[1]
                target = dt.now() + _kinds[kind](num)
                self.validateInput(target)
        except Exception as e:
            print(e)
            self.validateInput(None)

    def start(self):
        logging.debug("#start")
        if self.target is not None:
            logging.debug("new target: "+str(self.target))
            with open(rand_file(),'w+') as f:
                f.write(str(self.target))                
        else:
            print("No reminder set.")
        logging.debug("closing gui")
        self.master.quit()

def showGui():
    try:
        root = Tk()
        root.attributes('-type', 'dialog')
        ReminderGUI(root)
        root.mainloop()
        root.destroy()
    except Exception as e:
        logging.debug(e)
# -----
class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        self.cnt=0
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self._text)
        )
        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd=self._onClick)
    
    def _onClick(self,*args,**kwargs):
        logging.debug("onClick")
        showGui()

    def _text(self,*args,**kwargs):
        return f'{self.cnt}'

    def update(*args,**kwargs):
        reminders = [f for f in listdir(path) if f[0:2]=='r-']
        # ToDo: iterate reminders checking their values
