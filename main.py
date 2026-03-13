from pynput import keyboard

def on_press(key):
    try:
        if key.char is not None:
            print(key.char)
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()