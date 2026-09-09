# ⚡ LiveSpeed

> Real-time, minimal words-per-minute (WPM) monitor that lives directly in your system tray.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**LiveSpeed** monitors your global keystrokes in the background and dynamically renders your current typing speed right into the Windows Taskbar tray, macOS Menu Bar, or Linux system tray. Designed to look as clean and legible as native hardware monitors.

---

## ✨ Features

- **⚡ Real-Time WPM Engine:** Accurately measures cadence using a standard 5 keystrokes/word metric over a rolling time window.
- **🌊 Exponential Moving Average (EMA):** Smooths out micro-pauses between words so the display remains readable without rapid, jittery number jumping.
- **📉 Natural Idle Decay:** Automatically fades the speed back to zero when you stop typing.
- **🔍 Native Tray Typography:** Crisp, pure-white anti-aliased font rendering specifically tuned for high-DPI system trays (no muddy outlines or blurry scaling).
- **🎛️ Tray Context Menu:** Right-click the icon to view status, reset recorded statistics, or cleanly exit.
- **🛑 Global Kill Switch:** Press <kbd>F8</kbd> from any application to immediately stop and exit.

---

## 📁 Project Structure

```
livespeed/
├── main.py              # Application entry point & tray menu coordinator
├── tracker.py           # Thread-safe keystroke listener & WPM math engine
├── icon.py              # Dynamic tray icon generator with OS font fallbacks
├── config.py            # User-tunable parameters (smoothing, decay, window size)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Speedbird849/livespeed.git
cd livespeed
```

### 2. Set up a virtual environment (recommended)
```bash
python3 -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run LiveSpeed
```bash
python main.py
```

---

## 🔒 Operating System Permissions

LiveSpeed uses `pynput` to listen to global keystrokes across applications:

### **macOS**
macOS requires explicit **Accessibility** permission for global key events:
1. Open **System Settings** → **Privacy & Security** → **Accessibility**.
2. Enable your terminal emulator (e.g., *Terminal*, *iTerm2*, or *VS Code*) or your Python binary.
3. If keystrokes are not registering, restart the terminal after granting permissions.

### **Windows**
No special permissions required. Works out of the box on Windows 10 and 11.

### **Linux**
- Works natively on **X11** sessions.
- On **Wayland**, global key listeners are restricted by default compositor security policies. Run under an X11 session or configure appropriate `uinput`/`evdev` permissions.

---

## ⚙️ Configuration

You can easily customize LiveSpeed's responsiveness and appearance by editing `config.py`:

| Parameter | Default | Description |
| :--- | :---: | :--- |
| `WINDOW_SECONDS` | `3.0` | Duration of the rolling window for keystroke history. |
| `EMA_ALPHA` | `0.25` | Smoothing weight (0.0 to 1.0). Lower = smoother; Higher = more reactive. |
| `DECAY_RATE` | `0.75` | Speed multiplier applied per tick when idle to smoothly drop to 0. |
| `IDLE_TIMEOUT` | `0.8` | Inactivity threshold in seconds before decay begins. |
| `REFRESH_INTERVAL`| `0.2` | Tray icon refresh interval in seconds (5 Hz). |
| `ICON_SIZE` | `32` | Canvas dimension in pixels (32×32 optimal for high-DPI trays). |
| `HOTKEY_EXIT` | `"f8"` | Global emergency kill switch hotkey. |

---

## 📐 How It Works

1. **Keystroke Recording:** Keystrokes (letters, numbers, space, punctuation, and backspace) are captured globally and timestamped with high-precision monotonic time into a thread-safe sliding buffer.
2. **Rolling Speed Calculation:**
   $$\text{Instant WPM} = \frac{\text{Keystrokes in Window} / 5.0}{\Delta t_{\text{minutes}}}$$
3. **Smoothing & Decay:**
   $$\text{Speed}_t = \alpha \cdot \text{WPM} + (1 - \alpha) \cdot \text{Speed}_{t-1}$$
   When inactivity exceeds `IDLE_TIMEOUT`, speed smoothly decays via $\text{Speed}_t = \text{Speed}_{t-1} \times \text{DECAY\_RATE}$.
4. **Rendering:** Text is dynamically sized (larger for 1–2 digits, auto-scaled for 3+ digits) and rendered in pure white onto an uncompressed 32×32 RGBA canvas using native UI fonts (Segoe UI on Windows, SF Pro/Helvetica on macOS).

---

## 📜 License

Distributed under the MIT License. Feel free to modify and share!
