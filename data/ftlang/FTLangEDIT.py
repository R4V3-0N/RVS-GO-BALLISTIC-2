from tkinter import *
import threading
import time

from ftlang.compile import compile as comp
from ftlang.decompile import decompile as decomp
from ftlang.data import openwith

threads = []

def parallel(fn):
    def inner(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return inner

root = Tk()

last_ftlang = None
last_xml = None

def update_ftlang():
    global last_xml

    begin = time.time()
    src = txt_xml.get(1.0, END)
    if src == last_xml:
        root.after(500, update_ftlang)
        return
    last_xml = src

    try:
        lines = decomp(src)
    except Exception as e:
        root.after(1000, update_ftlang)
        # print(str(e))
        return
    
    key = txt_ftlang.index(INSERT)

    for n, line in enumerate(lines):
        line_no = float(n)
        txt_ftlang.replace(line_no+1, line_no+1, line)

    txt_ftlang.replace(float(len(lines))+1, END, '')
    
    txt_ftlang.mark_set(INSERT, key)

    end = time.time()
    took_secs = (end - begin)
    took_secs *= 10
    root.after(int(took_secs * 1000), update_ftlang)

def update_xml():
    global last_ftlang
    begin = time.time()
    src = txt_ftlang.get(1.0, END)

    if src == last_ftlang:
        root.after(500, update_xml)
        return
    last_ftlang = src
    
    try:
        lines = comp(src).split('\n')
    except Exception as e:
        root.after(1000, update_xml)
        # print(str(e))
        return
    
    key = txt_xml.index(INSERT)

    for n, line in enumerate(lines):
        line_no = float(n)
        txt_xml.replace(line_no+1, line_no+1, line.replace('\t', '     ') + '\n')

    txt_xml.replace(float(len(lines))+1, END, '')

    txt_xml.mark_set(INSERT, key)

    end = time.time()
    took_secs = (end - begin)
    took_secs *= 10
    root.after(int(took_secs * 1000), update_xml)

Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)

#Create & Configure frame 
frame=Frame(root)
frame.grid(row=0, column=0, sticky=N+S+E+W)

#Create a 5x10 (rows x columns) grid of buttons inside the frame
Grid.rowconfigure(frame, 0, weight=1)

Grid.columnconfigure(frame, 0, weight=1)
txt_ftlang = Text(frame)
txt_ftlang.grid(row=0, column=0, sticky=N+S+E+W) 

Grid.columnconfigure(frame, 1, weight=1)
txt_xml = Text(frame)
txt_xml.insert(END, openwith)
txt_xml.grid(row=0, column=1, sticky=N+S+E+W)  


update_xml()
update_ftlang()
root.mainloop()
