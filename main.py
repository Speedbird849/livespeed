from pynput import keyboard
from collections import deque
import threading
import time

def on_press(key):
    global last
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

    elapsed = (times[-1] - times[0]) / 60
    if (elapsed == 0): 
        return 0
    return int((len(times) / 5) / elapsed)

def display_loop():
    global speed
    while True:
        if (time.monotonic() - last > 0.5):
            speed = int(speed*0.75)
        else:
            speed = calculate_wpm()
        print(speed)
        time.sleep(0.2)

t = threading.Thread(target=display_loop, daemon=True)
t.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
