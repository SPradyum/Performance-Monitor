# ⚡ Performance Monitor

A futuristic **real-time system monitoring dashboard** built with **Python**, featuring a **neon cyberpunk UI** inspired by **MSI Afterburner / NZXT CAM / Rainmeter**.  
It displays live **CPU, GPU, RAM, Disk, Network, Temperature, and Battery** statistics with **animated circular performance gauges** and an **always-on-top mini overlay HUD** for quick monitoring over gameplay or multitasking.

---

## 🚀 Features

### 🔥 Performance Monitoring
- CPU usage + per-second live refresh
- **GPU usage + VRAM + temperature** (via `GPUtil`)
- RAM usage gauge
- Disk storage usage bar
- Upload & download network speed
- CPU & GPU temperature tracking
- Battery status + time remaining

### 🖥 Futuristic UI
- **Cyberpunk neon Purple/Blue theme**
- Custom **circular gauge UI components**
- Smooth indicator updates (1-second refresh)
- Modern dashboard layout using `customtkinter`
- **Mini Overlay HUD** always on top (toggle switch)

### 🌐 Overlay HUD
- Visible while gaming or multi-tasking
- Displays CPU%, GPU%, RAM, network speed
- Lightweight transparent system tray feel

---

## 🧰 Tech Stack & Libraries

| Library | Purpose |
|--------|---------|
| `customtkinter` | Modern themed GUI |
| `psutil` | System stats, CPU/RAM/Disk/Network/Battery |
| `GPUtil` | GPU load, temp, and memory |
| `matplotlib` | For future real-time performance graphs |
| `tkinter` | Canvas used for neon circular gauges |
---
## Install dependencies:
```bash
pip install customtkinter psutil GPUtil matplotlib
```
---
## 🧠 GPU & Temp Compatibility Notes

= GPU metrics require supported hardware and updated drivers.
- NVIDIA cards typically return full stats.
- AMD & integrated GPUs may show partial N/A depending on system.
---
## 🧱 Future Upgrades (Roadmap)
- 📈 Real-time animated line charts (CPU / GPU / RAM / NET)
- 🔔 Threshold alerts + sound & popup notification system
- 🎚 Fan RPM monitoring & control integration
- 🎨 Dynamic color theme selector
- 🌍 Web dashboard server mode (monitor from mobile)
---
## 🏆 Ideal For

- Gamers who want a floating overlay performance tracker
- Python GUI & system programming learners
- PC performance analysis / debugging / live benchmarking
- Portfolio or resume highlight project
---
## ⭐ Support

If you like this project, consider:

⭐ Starring the GitHub repo

🎁 Sharing feedback & feature requests
