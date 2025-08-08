import screen_brightness_control as sbc
import pyautogui
import screeninfo

GRID_SIZE = 26

def brightness_control(is_plus):
    #monitor_idx= get_cur_monitor_idx()
    monitor_idx=1
    print("monitor_idx",monitor_idx)
    brightness=sbc.get_brightness(display=monitor_idx)[0]
    print('b',brightness)
    brightness=brightness + 10 if is_plus else brightness - 10
    sbc.set_brightness(brightness, display=monitor_idx)

#pyautogui doesnt have paste so we use this
def get_clipboard():
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        return 'pyperclip module not installed'

def get_current_monitor():
    screens = screeninfo.get_monitors()
    x, y = pyautogui.position()
    for s in screens:
        if s.x <= x < s.x + s.width and s.y <= y < s.y + s.height:
            return s
    return screens[0] if screens else None

def get_cur_monitor_idx():
    screens = screeninfo.get_monitors()
    x, y = pyautogui.position()
    for idx, s in enumerate(screens):
        if s.x <= x < s.x + s.width and s.y <= y < s.y + s.height:
            return idx
    return 0 if screens else None

def screen_center():
    screens = screeninfo.get_monitors()
    if len(screens) < 2:
        return
    x, y = pyautogui.position()
    current_screen = None
    for s in screens:
        if s.x <= x < s.x + s.width and s.y <= y < s.y + s.height:
            current_screen = s
            break
    if not current_screen:
        return
    other_screen = [s for s in screens if s != current_screen]
    if not other_screen:
        return
    target = other_screen[0]
    center_x = target.x + target.width // 2
    center_y = target.y + target.height // 2
    pyautogui.moveTo(center_x, center_y)

def mouseless_click(k, k2):
    row = ord(k2.lower()) - 97 if isinstance(k2, str) and len(k2) == 1 and k2.isalpha() else -1
    col = ord(k.lower()) - 97 if isinstance(k, str) and len(k) == 1 and k.isalpha() else -1
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        monitor = get_current_monitor()
        monitor_x = monitor.x
        monitor_y = monitor.y
        sw = monitor.width
        sh = monitor.height

        cw = sw / GRID_SIZE
        ch = sh / GRID_SIZE

        # Default to center of the cell
        cx = (col + 0.5) * cw
        cy = (row + 0.5) * ch

        abs_cx = monitor_x + cx
        abs_cy = monitor_y + cy

        pyautogui.moveTo(abs_cx, abs_cy)
        pyautogui.click(abs_cx, abs_cy)
