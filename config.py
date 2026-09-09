"""LiveSpeed configuration constants and tuning parameters."""

# Keystroke calculation window in seconds
WINDOW_SECONDS = 1.0

# Exponential Moving Average smoothing factor when actively typing (0.0 - 1.0)
EMA_ALPHA = 0.25

# Idle decay multiplier applied every refresh tick when inactive
DECAY_RATE = 0.75

# Seconds of inactivity before WPM begins decaying towards 0
IDLE_TIMEOUT = 0.8

# Tray icon update interval in seconds (5 Hz)
REFRESH_INTERVAL = 0.2

# Tray icon dimension in pixels (32x32 is ideal for modern high-DPI trays)
ICON_SIZE = 32

# Number of keystrokes that constitute a standard "word"
CHARS_PER_WORD = 5.0

# Hotkey to immediately terminate LiveSpeed
HOTKEY_EXIT = "f8"

