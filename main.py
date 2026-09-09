import threading
import time
import pystray
from pystray import MenuItem as item

import config
from icon import create_tray_icon
from tracker import WPMTracker

def main():
    running = True

    def on_exit(icon=None, item=None):
        nonlocal running
        running = False
        tracker.stop()
        if icon:
            icon.stop()

    def on_reset(icon=None, item=None):
        tracker.reset()

    tracker = WPMTracker(on_exit=lambda: on_exit(tray_icon))

    menu = pystray.Menu(
        item("LiveSpeed WPM", None, enabled=False),
        pystray.Menu.SEPARATOR,
        item("Reset Stats", on_reset),
        item(f"Exit ({config.HOTKEY_EXIT.upper()})", on_exit)
    )

    tray_icon = pystray.Icon(
        name="livespeed",
        icon=create_tray_icon(0),
        title="LiveSpeed: 0 WPM",
        menu=menu
    )

    def display_loop():
        while running:
            speed = tracker.update_and_get_speed()
            rounded_speed = int(round(speed))

            tray_icon.icon = create_tray_icon(speed)
            tray_icon.title = f"LiveSpeed: {rounded_speed} WPM"
            time.sleep(config.REFRESH_INTERVAL)

    # Start keyboard hook & display worker threads
    tracker.start()
    update_thread = threading.Thread(target=display_loop, daemon=True)
    update_thread.start()

    # Main thread runs the system tray event loop
    try:
        tray_icon.run()
    finally:
        on_exit(tray_icon)

if __name__ == "__main__":
    main()