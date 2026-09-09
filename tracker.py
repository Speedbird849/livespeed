from collections import deque
import threading
import time
from typing import Callable, Optional
from pynput import keyboard

import config

class WPMTracker:
    """Thread-safe keystroke tracker and WPM calculator."""

    def __init__(self, on_exit: Optional[Callable[[], None]] = None):
        self._times = deque()
        self._speed = 0.0
        self._last_keypress = 0.0
        self._lock = threading.Lock()
        self._listener: Optional[keyboard.Listener] = None
        self._on_exit = on_exit

    def _is_countable_key(self, key) -> bool:
        """Check if the pressed key represents a valid typing stroke."""
        # Standard character keys (letters, numbers, symbols)
        if hasattr(key, "char") and key.char is not None:
            return True
        # Whitespace and editing keys integral to typing
        if key in (keyboard.Key.space, keyboard.Key.enter, keyboard.Key.backspace, keyboard.Key.tab):
            return True
        return False

    def _on_press(self, key):
        # Check for kill switch
        if key == getattr(keyboard.Key, config.HOTKEY_EXIT, keyboard.Key.f8):
            if self._on_exit:
                self._on_exit()
            return False

        if self._is_countable_key(key):
            now = time.monotonic()
            with self._lock:
                self._times.append(now)
                self._last_keypress = now

    def _calculate_instant_wpm(self) -> float:
        """Calculate rolling WPM over the sliding time window."""
        now = time.monotonic()
        cutoff = now - config.WINDOW_SECONDS

        with self._lock:
            while self._times and self._times[0] < cutoff:
                self._times.popleft()

            if not self._times:
                return 0.0

            # Guard against division by near-zero duration on sudden bursts
            duration = max(now - self._times[0], 1.0)
            keystrokes = len(self._times)

        words = keystrokes / config.CHARS_PER_WORD
        minutes = duration / 60.0
        return words / minutes

    def update_and_get_speed(self) -> float:
        """Update EMA speed and decay, returning the current smoothed WPM."""
        now = time.monotonic()
        with self._lock:
            is_idle = (now - self._last_keypress) > config.IDLE_TIMEOUT

        if is_idle:
            self._speed *= config.DECAY_RATE
            if self._speed < 1.0:
                self._speed = 0.0
        else:
            raw_wpm = self._calculate_instant_wpm()
            self._speed = config.EMA_ALPHA * raw_wpm + (1.0 - config.EMA_ALPHA) * self._speed

        return self._speed

    def reset(self):
        """Reset the recorded keystrokes and speed to zero."""
        with self._lock:
            self._times.clear()
            self._speed = 0.0
            self._last_keypress = 0.0

    def start(self):
        """Start listening to keyboard events in background."""
        if self._listener is None or not self._listener.is_alive():
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.daemon = True
            self._listener.start()

    def stop(self):
        """Stop listening to keyboard events."""
        if self._listener and self._listener.is_alive():
            self._listener.stop()
            self._listener = None

