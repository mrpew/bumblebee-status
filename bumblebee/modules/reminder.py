"""
    Reminder - a simple reminder widget for bumblebee <W I P>

        TODO:
                - add UI to view/edit/remove current reminders
                - switch to/add support for a UI toolkit that does not look like 1837

"""

# override print to make sure we ntarget_varer write to stdout (this would break i3bar)
# do this before importing any modules (besides logging).
import logging
def print(v):
    logging.debug(v)


import bumblebee.input
import bumblebee.output
import bumblebee.engine
from tkinter import Tk,Button,Label,Entry,StringVar
from datetime import datetime as dt, timedelta
from os import getenv, makedirs, listdir, remove
from random import random

# Make sure .reminder exists in ~
path = getenv("HOME") + "/.reminder"
try:
    makedirs(path)
except Exception as e:
    logging.debug(e)

# Random file name.
def rand_file():
    return path + '/r-' + '-'.join([ str( int (random() * 10000 ) ) for _ in range(3)])


_time_types = {
    "h": lambda n: timedelta(hours=n),
    "m": lambda n: timedelta(minutes=n),
    "s": lambda n: timedelta(seconds=n),
}

# GUI Class
class CreateReminderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Reminder")
        self.label = Label(master, text="PyReminder")
        self.label.pack()
        self.start_button = Button(master, text="Start", command=self.start)
        self.start_button.pack()
        # Target = reminder date/time
        self.target_var = StringVar()
        self.target_var.trace_add("write", self.parse)
        self.target_e = Entry(master,textvariable=self.target_var)
        self.target_e.pack()
        self.target_var.set("10 m")
        # Message = message to show
        self.msg_var = StringVar()        
        self.msg_e = Entry(master,textvariable=self.msg_var)
        self.msg_e.pack()
        self.msg_var.set("Message")
                
        
    def validateInput(self,value):
        if value is not None:
            self.target_e.config(background="green")
        else:
            self.target_e.config(background="red")
        self.target = value

    def parse(*args,**kwargs):
        self = args[0]
        try:
            text = self.target_var.get().strip()
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
                target = dt.now() + _time_types[kind](num)
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
                f.write("\n")
                f.write(self.msg_var.get())
        else:
            print("No reminder set.")
        logging.debug("closing gui")
        self.master.quit()

# GUI Class: Reminder Window that pops up around the reminder time.
class ReminderGUI:
     def __init__(self, master,text):
        self.master = master
        master.title("Reminder")
        self.label = Label(master, text=text)
        self.label.pack()
        self.dismiss_button = Button(master, text="dismiss", command=self.master.quit)
        self.dismiss_button.pack()


# Show the GUI to create a new reminder
def showGuiCreateReminder():
    try:
        root = Tk()
        root.attributes('-type', 'dialog')
        CreateReminderGUI(root)
        root.mainloop()
        root.destroy()
    except Exception as e:
        logging.debug(e)


# Show the GUI to create a new reminder
def showReminder(text):
    try:
        root = Tk()
        root.attributes('-type', 'dialog')
        ReminderGUI(root,text)
        root.mainloop()
        root.destroy()
    except Exception as e:
        logging.debug(e)


# Bumblebee module class
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
        showGuiCreateReminder()

    def _text(self,*args,**kwargs):
        return f'⏰ {self.cnt}'

    def update(self,*args,**kwargs):
        reminders = [f for f in listdir(path) if f[0:2]=='r-']
        self.cnt = len(reminders)
        for re in reminders:
            re_path = path+'/'+re
            fire=False
            with open(re_path,'r') as rem:
                rtext = [l.strip() for l in rem.readlines()]
                date = dt.strptime(rtext[0],"%Y-%m-%d %H:%M:%S.%f")
                now = dt.now()
                if date < now:
                    fire=True
            if fire:
                remove(re_path)
                showReminder(rtext[1])

