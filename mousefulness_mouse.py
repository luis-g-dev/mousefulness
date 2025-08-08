import mouseful_menus as menus
import mousefulness_functions as fn
import tkinter as tk
import mouse
import math
import time

BG = "black"
TRANSPARENCY = 1.0
INNER_RADIUS = 0
OUTER_RADIUS = 0

current_menu = None
has_overlay = False
overlay = None
m_canvas = None
root = None

def create_overlay():
    global has_overlay, overlay, m_canvas
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

    m_canvas = tk.Canvas(overlay, width=sw, height=sh, bg=BG)
    m_canvas.pack(fill="both", expand=True)
    m_canvas.bind("delete", lambda _: root.quit())
    # Ensure the window/canvas are realized before drawing so centering uses real sizes
    overlay.update_idletasks()
    m_canvas.update_idletasks()

    # Set a sensible outer radius based on the current screen size
    global OUTER_RADIUS
    try:
        OUTER_RADIUS = min(sw, sh) // 4
    except Exception:
        OUTER_RADIUS = 0

    # Draw only after the canvas has a real size to ensure proper centering
    def _initial_draw_when_ready():
        w, h = m_canvas.winfo_width(), m_canvas.winfo_height()
        if w <= 1 or h <= 1:
            overlay.after(20, _initial_draw_when_ready)
            return
        draw_main_menu_overlay()

    overlay.after(0, _initial_draw_when_ready)

def hide_menu():
    destroy_overlay()

def old_hide_menu():
    destroy_overlay()

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    overlay.geometry(f"{sw}x{sh}+0+0")
    overlay.focus_force()
    canvas = tk.Canvas(overlay, width=sw, height=sh, bg=BG, highlightthickness=0)
    canvas.pack()
    draw_main_menu_overlay()

def destroy_overlay():
    global has_overlay,overlay
    has_overlay=False
    overlay.destroy()

def draw_main_menu_overlay():
    global current_menu
    menus.draw_menu(m_canvas, menu_type="main", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
    m_canvas.bind("<Button-1>", handle_main_click)
    m_canvas.bind("<Motion>", handle_main_motion)
    current_menu = "main"

def draw_mods_menu_overlay():
    global current_menu
    menus.draw_menu(m_canvas, menu_type="mods", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
    m_canvas.bind("<Button-1>", handle_mods_click)
    m_canvas.bind("<Motion>", handle_mods_motion)
    current_menu = "mods"

def draw_fn_menu_overlay():
    global current_menu
    menus.draw_menu(m_canvas, menu_type="fn", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
    m_canvas.bind("<Button-1>", handle_fn_click)
    m_canvas.bind("<Motion>", handle_fn_motion)
    current_menu = "fn"

def draw_keys_menu_overlay():
    global current_menu
    menus.draw_menu(m_canvas, menu_type="keys", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
    m_canvas.bind("<Button-1>", handle_keys_click)
    m_canvas.bind("<Motion>", handle_keys_motion)
    current_menu = "keys"

def handle_main_click(ev):
    x, y = ev.x, ev.y
    cx, cy = root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2
    distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    back_font = ("Arial", 18, "bold")
    BACK_RADIUS = menus.get_back_radius(m_canvas, cx, cy, back_font)
    if distance <= BACK_RADIUS:
        hide_menu()
        return
    angle = math.degrees(math.atan2(cy - y, x - cx))
    angle = (angle + 360) % 360
    n = 6
    sector = int(angle // (360 / n))
    if sector == 0:
        hide_menu()  # Close
    elif sector == 1:
        draw_mods_menu_overlay()
    elif sector == 2:
        draw_fn_menu_overlay()
    elif sector == 3:
        # Subsector: which sub-sector?
        sub_spacing = (OUTER_RADIUS - (BACK_RADIUS + 8)) / 4
        sub_distance = distance - (BACK_RADIUS + 8)
        sub_idx = int(sub_distance // sub_spacing)
        print(f"Subsector {sub_idx+1} selected")
        hide_menu()
    elif sector == 4:
        draw_keys_menu_overlay()
    elif sector == 5:
        print("Menu Type toggled")
        hide_menu()

def handle_main_motion(ev):
    menus.highlight_menu(m_canvas, ev, menu_type="main", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
def handle_fn_motion(ev):
    menus.highlight_menu(m_canvas, ev, menu_type="fn", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
def handle_mods_motion(ev):
    menus.highlight_menu(m_canvas, ev, menu_type="mods", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
def handle_keys_motion(ev):
    menus.highlight_menu(m_canvas, ev, menu_type="keys", inner_radius=INNER_RADIUS, outer_radius=OUTER_RADIUS)
def handle_mods_motion(ev):
    pass

def handle_mods_click(ev):
    x, y = ev.x, ev.y
    cx, cy = root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2
    distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    back_font = ("Arial", 18, "bold")
    BACK_RADIUS = menus.get_back_radius(m_canvas, cx, cy, back_font)
    if distance <= BACK_RADIUS:
        draw_main_menu_overlay()
        return
    angle = math.degrees(math.atan2(cy - y, x - cx))
    angle = (angle + 360) % 360
    n = 5
    sector = int(angle // (360 / n))
    print(["Ctrl", "Alt", "Shift", "Win", "Back"][sector], "mod selected")
    hide_menu()

def handle_fn_click(ev):
    x, y = ev.x, ev.y
    cx, cy = root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2
    distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    back_font = ("Arial", 18, "bold")
    BACK_RADIUS = menus.get_back_radius(m_canvas, cx, cy, back_font)
    if distance <= BACK_RADIUS:
        draw_main_menu_overlay()
        return
    angle = math.degrees(math.atan2(cy - y, x - cx))
    angle = (angle + 360) % 360
    n = 13
    sector = int(angle // (360 / n))
    print(f"F{sector+1} selected" if sector < 12 else "Back")
    hide_menu()

def handle_keys_click(ev):
    x, y = ev.x, ev.y
    cx, cy = root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2
    distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    back_font = ("Arial", 18, "bold")
    BACK_RADIUS = menus.get_back_radius(m_canvas, cx, cy, back_font)
    if distance <= BACK_RADIUS:
        draw_main_menu_overlay()
        return
    angle = math.degrees(math.atan2(cy - y, x - cx))
    angle = (angle + 360) % 360
    num_rings = 2
    ring_spacing = (OUTER_RADIUS - INNER_RADIUS) / num_rings
    inner_ring = ["Fn", "Numbers", "Quotes", "Alt#"]
    outer_ring = ["Bars", "Browser", "Media", "Symbols", "CMD"]
    for ring_idx, items in enumerate([inner_ring, outer_ring]):
        inner_r = INNER_RADIUS + ring_idx * ring_spacing
        outer_r = INNER_RADIUS + (ring_idx + 1) * ring_spacing
        n = len(items)
        for i, label in enumerate(items):
            start = i * 360 / n
            end = (i + 1) * 360 / n
            if inner_r < distance < outer_r and start <= angle < end:
                print(f"Keys submenu: {label}")
                hide_menu()
                return

def handle_keys_motion(ev):
    pass

last_mid_click_time = 0
mid_click_interval = 1 # seconds
def on_middle_click():
    print('on_middle_click')
    global last_mid_click_time
    now = time.time()
    if now - last_mid_click_time < mid_click_interval:
        if has_overlay:
            hide_menu()
        else:
            root.after(0, create_overlay)
        last_mid_click_time = 0
    else:
        last_mid_click_time = now

if __name__ == "__main__":
    mouse.on_middle_click(on_middle_click)

    root = tk.Tk()

    screen_radius = min(root.winfo_screenwidth(), root.winfo_screenheight()) // 4
    OUTER_RADIUS = screen_radius

    root.withdraw()
    root.mainloop()
