from pynput import keyboard
from collections import deque
import time

def on_press(key):
    try:
        if key.char is not None:
            times.append(time.monotonic())
            print(calculate_wpm())
    except AttributeError:
        pass

times = deque()

window = 3

def calculate_wpm():
    now = time.monotonic()
    cutoff = now - window

    if not times:
        return 0

    while (times and times[0] < cutoff):
        times.popleft()

    return int((len(times) / 5) / (window / 60))

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
