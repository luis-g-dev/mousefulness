import keyboard
import time

HOME_ROW_MODS = {
    'a': {'tap': 'a', 'hold': 'left alt'},
    's': {'tap': 's', 'hold': 'left shift'},
    'd': {'tap': 'd', 'hold': 'left windows'},
    'f': {'tap': 'f', 'hold': 'left ctrl'},
    'j': {'tap': 'j', 'hold': 'right ctrl'},
    'k': {'tap': 'k', 'hold': 'right windows'},
    'l': {'tap': 'l', 'hold': 'right shift'},
    'ç': {'tap': 'ç', 'hold': 'alt gr'},
    'space': {'tap': 'space', 'hold': 'shift'},
    'caps lock': {'tap': 'a', 'hold': 'esc'},
    'esc': {'tap': 'esc', 'hold': 'caps lock'},
}

THRES_HOLD = .05

STILL_HOLD='is_still_holding'
IS_HOLD='is_holding'
IS_FIRST='is_releasing_before_other_k'
IS_TAP='is_tap_hold_ready'
TAP='tap_time'
T='t'

holds = {k: {T: None, IS_HOLD: False, STILL_HOLD:False, IS_FIRST:False, TAP:None} for k in HOME_ROW_MODS}

special_fn = None

def on_press(e):
    k = e.name
    if k is None:
        return True

    if special_fn is not None:
        handled = special_fn(k, 'press') 
        if handled:
            return False  # Suppress the key
        
    k = k.lower() if k.lower() in HOME_ROW_MODS else k
    if k in HOME_ROW_MODS:
        holds[k][IS_TAP] = time.time
        if not holds[k][IS_HOLD]:
            holds[k][IS_HOLD] = True
            holds[k][T] = time.time()
            return False
        duration = time.time() - holds[k][T] if holds[k][T] is not None else 0
        if duration > THRES_HOLD:
            holds[k][STILL_HOLD] = True
            if holds[k][TAP]:
                keyboard.press_and_release(HOME_ROW_MODS[k]['tap'])
                return False
            keyboard.press(HOME_ROW_MODS[k]['hold'])
            return False
        return False
    
    for hold in holds:
        holds[hold][TAP] = None
        if holds[hold][STILL_HOLD]:
            continue
        if holds[hold][IS_HOLD]:
            keyboard.press_and_release(hold)
            holds[hold].update({STILL_HOLD: False, IS_HOLD: False, T: None, IS_FIRST: True})
    return True

def on_release(e):
    k = e.name
    if k is None:
        return True

    if special_fn is not None:
        handled = special_fn(k, 'release') 
        if handled:
            return False  # Suppress the key
    
    for hold in holds:
        holds[hold][TAP] = None

    k = k.lower() if k.lower() in HOME_ROW_MODS else k
    if k in HOME_ROW_MODS:
        if holds[k][STILL_HOLD]:
            keyboard.release(HOME_ROW_MODS[k]['hold'])
            holds[k].update({STILL_HOLD: False, IS_HOLD: False, T: None})
            return False
        holds[k][IS_HOLD] = False
        if holds[k][IS_FIRST]:
            holds[k][IS_FIRST] = False
            return False
        keyboard.press_and_release(HOME_ROW_MODS[k]['tap'])
        if holds[k][TAP] is None:
            holds[k][TAP] = time.time()
        return False
    return True

def listen():
    keyboard.on_press(on_press, suppress=True)
    keyboard.on_release(on_release, suppress=True)

if __name__ == "__main__":
    listen()

    def setup():
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.mainloop()
    setup()
