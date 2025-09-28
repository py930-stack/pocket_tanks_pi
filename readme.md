# Pocket Tanks (Lite) – Raspberry Pi 4 Edition

A fun artillery game inspired by **Pocket Tanks**, built in **Python + Pygame**.  
Designed to run smoothly on Raspberry Pi 4 — download, install, and play!

![screenshot](https://via.placeholder.com/800x400?text=Pocket+Tanks+Lite+Screenshot)

---

## 🎮 Features

- Two-player **hot-seat gameplay** (or optional AI opponent)
- **Destructible terrain** with craters from explosions
- **Simple physics** with wind & gravity
- **Score tracking**
- Runs at 60 FPS on Raspberry Pi 4

---

## 🎯 Controls

### Player 1
- `← / →` Adjust angle
- `↑ / ↓` Adjust power
- `Space` Fire

### Player 2
- `A / D` Adjust angle
- `W / S` Adjust power
- `Left Ctrl` Fire

### General
- `N` New match
- `R` Regenerate terrain
- `T` Toggle AI for Player 2
- `ESC` Quit game

---

## 📦 Installation

### 1. Install system dependencies (Raspberry Pi OS)
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-dev     libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

### 2. Clone this repository
```bash
git clone https://github.com/py930-stack/pocket-tanks-pi.git
cd pocket-tanks-pi
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the game
```bash
python pocket_tanks_pi.py
```

Or enable AI for Player 2:
```bash
python pocket_tanks_pi.py --ai
```

---

## 🛠️ Troubleshooting

- If you see errors like `pygame.error: No available video device`,  
  make sure you’re running in a desktop environment (not SSH-only).  
- For laggy performance, lower resolution in `pocket_tanks_pi.py`:
  ```python
  WIDTH, HEIGHT = 800, 480   # smaller window for speed
  ```
- If `pygame-ce` doesn’t work, try classic `pygame`:
  ```bash
  pip install pygame
  ```

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.  
Ideas for improvements:
- Add more weapon types (cluster bombs, nukes, diggers)
- Tank health bars
- Sound effects
- Fancy terrain themes

---

## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 YOUR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## 🐧 Tested On

- Raspberry Pi 4 Model B (4GB) – Raspberry Pi OS (64-bit), Python 3.11, pygame-ce 2.4
- Should also work on Linux, Windows, and macOS with Python 3.9+

---

Enjoy blasting craters and experimenting with angles & power! 🚀💥