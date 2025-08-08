from mouseless.mouseless_config import CONFIG
import mousefulness_functions as fn
import mousefulness_keyboard as less_keyboard
import tkinter as tk
import pyautogui
import keyboard
import time

GRID_SIZE = CONFIG["grid_size"]
TRANSPARENCY = CONFIG["transparency"]
BG = "black"
FG = "gray"

sw, sh = None, None
has_overlay = False
overlay = None
mouseless_last_k = None  # Use separate last_k for mouseless
root = None

def is_letter(s):
    return isinstance(s, str) and len(s) == 1 and s.isalpha()

def destroy_overlay():
    global has_overlay,overlay
    has_overlay=False
    overlay.destroy()

def create_overlay():
    global has_overlay, overlay
    if has_overlay:
        return
    has_overlay = True

    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-alpha', TRANSPARENCY)
    overlay.focus_force()
    
    monitor = fn.get_current_monitor()
    if monitor:
        sw = monitor.width
        sh = monitor.height
        overlay.geometry(f"{sw}x{sh}+{monitor.x}+{monitor.y}")
    else:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        overlay.geometry(f"{sw}x{sh}+0+0")

    k_canvas = tk.Canvas(overlay, width=sw, height=sh, bg=BG)
    k_canvas.pack()

    cw = sw / GRID_SIZE
    ch = sh / GRID_SIZE
    font = ("Droid Sans Mono", min(int(cw), int(ch)) // 2)
    for i in range(GRID_SIZE + 1):
        k_canvas.create_line(round(i*cw), 0, round(i*cw), sh, fill=FG, width=1)
        k_canvas.create_line(0, round(i*ch), sw, round(i*ch), fill=FG, width=1)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            k_canvas.create_text(round((c+.5)*cw), round((r+.5)*ch), text=chr(65 + r) + chr(65 + c), fill=FG, font=font)
    k_canvas.bind("<Triple-Button-1>", lambda _: destroy_overlay())


def mouseless_keys(k, event_type):
    global has_overlay, overlay, mouseless_last_k
    
    if event_type != 'release':
        return False
    if k == 'ctrl' and mouseless_last_k == 'ctrl':
        had_overlay = False
        if has_overlay:
            had_overlay = True
            destroy_overlay()
        fn.screen_center()
        if had_overlay:
            root.after(0, create_overlay)  #prevent temp popup
        mouseless_last_k = None
        return False
    
    elif k == 'shift' and mouseless_last_k == 'shift':
        destroy_overlay() if has_overlay else root.after(0, create_overlay)
        mouseless_last_k = None
        return False
    
    elif has_overlay and is_letter(k) and is_letter(mouseless_last_k):
        destroy_overlay()
        fn.mouseless_click(k, mouseless_last_k)
        mouseless_last_k = None
        return True  
    
    elif has_overlay and mouseless_last_k == 'space' and k =='w':
        destroy_overlay()
        clipboard_text = fn.get_clipboard()
        for code in ['CR13', 'LF10', '0x0d', '0x0a','0x09','⟶']:
            clipboard_text = clipboard_text.replace(code, ' ')
        clipboard_text = clipboard_text.replace('\n', '  ')
        #pyautogui.write(clipboard_text)
        pyautogui.click()
        keyboard.write(clipboard_text, exact=True)
        mouseless_last_k = None
        return True  
    elif has_overlay and mouseless_last_k == 'space' and k == 'q':
        fn.brightness_control()
        mouseless_last_k = None
        return True  
    elif has_overlay and mouseless_last_k=='+'and k=='+':
        #sbc uses WMI (cannot be called from thread handling kb hooks/GUI evs (TK/keyboard)
        root.after(0, lambda: fn.brightness_control(True))
        mouseless_last_k=None
        return True
    elif has_overlay and mouseless_last_k=='-'and k=='-':
        root.after(0, lambda: fn.brightness_control(False))
        mouseless_last_k=None
        return True
    else:
        mouseless_last_k = k  # Update our own last_k
        return False  # Let keyboard module handle it

if __name__ == "__main__":
    less_keyboard.special_fn = mouseless_keys  # Connect the two modules
    less_keyboard.listen()  # Start listening for keyboard events

    root = tk.Tk()
    root.withdraw() 

    create_overlay()
    root.mainloop()
