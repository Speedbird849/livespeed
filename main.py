from pynput import keyboard

def press(key):
    print(key)

with keyboard.Listener(on_press=press) as listener:
    listener.join()