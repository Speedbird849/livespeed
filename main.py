from collections import deque
import platform
import threading
import time
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard
import pystray

# --- Configuration & State ---
WINDOW_SECONDS = 3.0   # Window duration for WPM calculation
times = deque()
speed = 0.0
last_keypress = 0.0
lock = threading.Lock()

# Cache font once across platforms
def load_font(size):
    system = platform.system()
    candidates = []
    if system == "Darwin":
        candidates = ["/System/Library/Fonts/SFNSMono.ttf", "/System/Library/Fonts/Menlo.ttc", "Helvetica.ttc"]
    elif system == "Windows":
        candidates = ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"]
    else:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

font_num = load_font(28)
font_lbl = load_font(16)

def on_press(key):
    global last_keypress
    if key == keyboard.Key.f8:
        icon.stop()
        return False

    # Count alphanumeric keys, symbols, space, and backspace
    is_valid_key = False
    if hasattr(key, 'char') and key.char is not None:
        is_valid_key = True
    elif key in (keyboard.Key.space, keyboard.Key.enter, keyboard.Key.backspace):
        is_valid_key = True

    if is_valid_key:
        now = time.monotonic()
        with lock:
            times.append(now)
            last_keypress = now

def calculate_wpm():
    now = time.monotonic()
    cutoff = now - WINDOW_SECONDS

    with lock:
        while times and times[0] < cutoff:
            times.popleft()

        if not times:
            return 0.0

        # Prevent division by tiny fractions when starting
        duration = max(now - times[0], 1.0)
        keystrokes = len(times)

    return (keystrokes / 5.0) / (duration / 60.0)

def create_icon(wpm):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    wpm_str = str(int(wpm))
    # Centered text drawing using anchor="mm"
    draw.text((32, 22), wpm_str, font=font_num, fill="white", stroke_width=2, stroke_fill="black", anchor="mm")
    draw.text((32, 50), "WPM", font=font_lbl, fill="#AAAAAA", stroke_width=1, stroke_fill="black", anchor="mm")
    return img

def display_loop():
    global speed
    while True:
        now = time.monotonic()
        if now - last_keypress > 0.8:
            speed = speed * 0.75  # Decay when idle
        else:
            speed = 0.25 * calculate_wpm() + 0.75 * speed  # EMA smooth

        if speed < 1:
            speed = 0

        icon.icon = create_icon(round(speed))
        time.sleep(0.2)

def keyboard_loop():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

icon = pystray.Icon("wpm", create_icon(0), "LiveSpeed WPM")

threading.Thread(target=display_loop, daemon=True).start()
threading.Thread(target=keyboard_loop, daemon=True).start()

icon.run()