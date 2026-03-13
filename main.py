from pynput import keyboard
from collections import deque
import threading
import time

def on_press(key):
    try:
        if key.char is not None:
            times.append(time.monotonic())
    except AttributeError:
        pass

times = deque()

window = 1

def calculate_wpm():
    now = time.monotonic()
    cutoff = now - window

    if not times:
        return 0

    while (times and times[0] < cutoff):
        times.popleft()

    return int((len(times) / 5) / (window / 60))

def display_loop():
    while True:
        print(calculate_wpm())
        time.sleep(0.2)

t = threading.Thread(target=display_loop, daemon=True)
t.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
