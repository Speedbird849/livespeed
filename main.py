from pynput import keyboard
from collections import deque
import threading
import time
import pystray
from PIL import Image, ImageDraw

def on_press(key):
    global last
    if (key == keyboard.Key.f1):
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
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 20), str(wpm), fill=(255, 255, 255, 255))
    return img

icon = pystray.Icon("wpm", create_icon(0), "WPM")

t = threading.Thread(target=display_loop, daemon=True)
t.start()

k = threading.Thread(target=keyboard_loop, daemon=True)
k.start()

icon.run()