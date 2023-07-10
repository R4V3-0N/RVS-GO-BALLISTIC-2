import tkinter as tk

from ftlang.compile import compile as comp
from ftlang.decompile import decompile as decomp
from ftlang.data import openwith

undo_buf = []
redo_buf = []

def txt_key_press(_):
    src = txt.get(1.0, tk.END)
    undo_buf.append(src)

def txt_set(obj, lines):
    if isinstance(lines, str):
        lines = lines.split('\n')

    key = obj.index(tk.INSERT)

    for n, line in enumerate(lines):
        line_no = float(n)
        obj.replace(line_no+1, line_no+1, line.replace('\t', '     ') + '\n')

    obj.replace(float(len(lines))+1, tk.END, '')
    
    obj.mark_set(tk.INSERT, key)


def update_ftlang():
    global redo_buf
    src = txt.get(1.0, tk.END)
    try:
        lines = decomp(src)
    except Exception as e:
        print(e)
        return
    
    txt_set(txt, lines)
    redo_buf = []
    undo_buf.append(src)

def update_xml():
    global redo_buf
    src = txt.get(1.0, tk.END)
    try:
        lines = comp(src).split('\n')
    except Exception as e:
        print(e)
        return
    
    txt_set(txt, lines)
    redo_buf = []
    undo_buf.append(src)

def txt_spaces(_):
    txt.insert(txt.index(tk.INSERT), "    ")
    return "break"

def undo(_):
    print(undo_buf)
    if len(undo_buf) != 0:
        redo_buf.append(txt.get(1.0, tk.END))
        txt_set(txt, undo_buf.pop())

def redo(_):
    print(redo_buf)
    if len(redo_buf) != 0:
        undo_buf.append(txt.get(1.0, tk.END))
        txt_set(txt, redo_buf.pop())

root = tk.Tk()
root.bind('<Control-z>', undo)
root.bind('<Control-Z>', redo)
root.bind('<Control-y>', redo)

win = tk.Frame(root)
win.pack(expand=True, fill=tk.BOTH)

txt_frame = tk.Frame(win)
txt_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

txt = tk.Text(txt_frame)
txt.pack(expand=True, fill=tk.BOTH)
txt.bind('<Tab>', txt_spaces)
txt.bind('<KeyPress>', txt_key_press)

buttons = tk.Frame(win)
buttons.pack(side=tk.TOP)

to_xml = tk.Button(buttons, text='to XML', command=update_xml)
to_xml.pack(side=tk.LEFT)

to_ftlang = tk.Button(buttons, text='to FTLang', command=update_ftlang)
to_ftlang.pack(side=tk.LEFT)

root.mainloop()
