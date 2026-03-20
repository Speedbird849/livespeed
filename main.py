from pynput import keyboard
from collections import deque
import threading
import time
import pystray
from PIL import Image, ImageDraw, ImageFont

def on_press(key):
    global last
    if (key == keyboard.Key.f1):
        icon.stop()
        return False
    try:
        if key.char is not None:
            times.append(time.monotonic())
            last = time.monotonic()
    except AttributeError:
        pass

times = deque()
speed = 0
last = 0
wpm_history = deque([0] * 300, maxlen=300)
graph_window = None

def calculate_wpm():
    now = time.monotonic()
    cutoff = now - 1

    if not times:
        return 0

    while (times and times[0] < cutoff):
        times.popleft()

    elapsed = (now - times[0]) / 60
    if (elapsed == 0): 
        return 0
    return int((len(times) / 5) / elapsed)

def display_loop():
    global speed
    while True:
        if (time.monotonic() - last > 0.5):
            speed = int(speed*0.75)
        else:
            speed = int(0.2 * calculate_wpm() + 0.8 * speed)
        print(speed)
        icon.icon = create_icon(speed)
        time.sleep(0.2)

def keyboard_loop():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def create_icon(wpm):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 36)
    x, y = 5, 0
    draw.text((x-1, y), str(wpm), font=font, fill="black")
    draw.text((x+1, y), str(wpm), font=font, fill="black")
    draw.text((x, y-1), str(wpm), font=font, fill="black")
    draw.text((x, y+1), str(wpm), font=font, fill="black")
    draw.text((x, y), str(wpm), font=font, fill="white")
    draw.text((x, y + 34), "WPM", font=font, fill="white")
    return img

class GraphWindow:
    W, H = 640, 300
    PAD = 40
    BG = "#0d0d0f"
    GRID = "#1e1e24"
    LINE = "#39ff8f"
    FILL = "#39ff8f22"
    TEXT = "#a0a0b0"
    FONT_LG = ("Consolas", 36, "bold")
    FONT_SM = ("Consolas", 10)
 
    def __init__(self):
        self.alive = True
        self.root = tk.Tk()
        self.root.title("WPM")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
 
        hdr = tk.Frame(self.root, bg=self.BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        self.lbl_wpm = tk.Label(hdr, text="0", fg="white", bg=self.BG, font=self.FONT_LG)
        self.lbl_wpm.pack(side="left")
        tk.Label(hdr, text=" WPM", fg=self.TEXT, bg=self.BG, font=("Consolas", 14)).pack(side="left", pady=(12, 0))
        self.lbl_peak = tk.Label(hdr, text="peak: 0", fg=self.TEXT, bg=self.BG, font=self.FONT_SM)
        self.lbl_peak.pack(side="right", pady=(18, 0))
 
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg=self.BG, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(8, 20))
 
        self.root.bind("<<Update>>", self._draw)
        self._draw()
        self.root.mainloop()
 
    def _close(self):
        global graph_window
        self.alive = False
        graph_window = None
        self.root.destroy()
 
    def _draw(self, _=None):
        c = self.canvas
        W, H, pad = self.W, self.H, self.PAD
        c.delete("all")
 
        data = list(wpm_history)
        peak = max(data) if data else 1
        y_max = max(peak * 1.2, 10)
        cur = data[-1] if data else 0
        plot_w = W - pad * 2
        plot_h = H - pad * 2
 
        for i in range(5):
            gy = pad + i * plot_h // 4
            c.create_line(pad, gy, W - pad, gy, fill=self.GRID)
            c.create_text(pad - 6, gy, text=str(int(y_max * (1 - i / 4))), anchor="e", fill=self.TEXT, font=self.FONT_SM)
 
        c.create_line(pad, H - pad, W - pad, H - pad, fill=self.GRID)
        c.create_text(pad, H - pad + 14, text="60s ago", anchor="w", fill=self.TEXT, font=self.FONT_SM)
        c.create_text(W - pad, H - pad + 14, text="now", anchor="e", fill=self.TEXT, font=self.FONT_SM)
 
        n = len(data)
        points = [(pad + int(i * plot_w / (n - 1)) if n > 1 else pad,
                   pad + plot_h - int(v / y_max * plot_h)) for i, v in enumerate(data)]
 
        flat_fill = [coord for pt in ([points[0]] + points + [(points[-1][0], H - pad), (pad, H - pad)]) for coord in pt]
        c.create_polygon(flat_fill, fill=self.FILL, outline="")
 
        if len(points) > 1:
            c.create_line([coord for pt in points for coord in pt], fill=self.LINE, width=2, smooth=True)
 
        ex, ey = points[-1]
        for r, a in [(8, "22"), (5, "55"), (3, "ff")]:
            c.create_oval(ex - r, ey - r, ex + r, ey + r, fill=self.LINE[:7] + a, outline="")
 
        self.lbl_wpm.config(text=str(cur))
        self.lbl_peak.config(text=f"peak: {peak}")
 
def open_graph():
    global graph_window
    if graph_window is not None and graph_window.alive:
        graph_window.root.lift()
        graph_window.root.focus_force()
        return
    threading.Thread(target=lambda: GraphWindow(), daemon=True).start()
 
icon = pystray.Icon(
    "wpm",
    create_icon(0),
    "WPM",
    menu=pystray.Menu(
        pystray.MenuItem("View graph", open_graph, default=True),
        pystray.MenuItem("Quit (F1)", lambda: icon.stop()),
    )
)

icon = pystray.Icon("wpm", create_icon(0), "WPM")

t = threading.Thread(target=display_loop, daemon=True)
t.start()

k = threading.Thread(target=keyboard_loop, daemon=True)
k.start()

icon.run()