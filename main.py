import time
import platform
from datetime import datetime

import psutil
import GPUtil
import customtkinter as ctk
import tkinter as tk


class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ======= THEME / COLORS =======
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.neon_purple = "#a855f7"
        self.neon_blue = "#22d3ee"
        self.bg_dark = "#020617"      # overall background
        self.card_dark = "#020617"    # card background
        self.card_border = "#1e293b"  # border color
        self.text_main = "#e5e7eb"
        self.text_muted = "#9ca3af"

        self.title("Performance Monitor")
        self.geometry("1120x650")
        self.resizable(False, False)
        self.configure(fg_color=self.bg_dark)

        # For network speed calculations
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

        # For CPU/GPU history (future charts)
        self.cpu_history = []
        self.gpu_history = []

        # Overlay flag
        self.overlay = None

        self._build_ui()
        self._create_overlay()

        # Start update loop
        self.update_stats()

    # ================== UI BUILDING ==================

    def _build_ui(self):
        # -------- HEADER --------
        header_frame = ctk.CTkFrame(self, fg_color=self.bg_dark, corner_radius=0)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ Performance Monitor",
            font=("Segoe UI", 24, "bold"),
            text_color=self.text_main
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="CPU · GPU · RAM · Disk · Network",
            font=("Segoe UI", 13),
            text_color=self.text_muted
        )
        subtitle_label.pack(side="left", padx=15)

        overlay_btn = ctk.CTkButton(
            header_frame,
            text="Widget",
            command=self._toggle_overlay,
            fg_color=self.neon_purple,
            hover_color="#7c3aed",
            corner_radius=20
        )
        overlay_btn.pack(side="right")

        # -------- MAIN LAYOUT --------
        main_frame = ctk.CTkFrame(self, fg_color=self.bg_dark, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Top cards row
        cards_frame = ctk.CTkFrame(main_frame, fg_color=self.bg_dark)
        cards_frame.pack(fill="x", pady=(0, 10))

        # Bottom info row
        bottom_frame = ctk.CTkFrame(main_frame, fg_color=self.bg_dark)
        bottom_frame.pack(fill="both", expand=True)

        # ---- TOP CARDS: CPU / GPU / RAM / DISK ----
        self.cpu_card = self._create_card(cards_frame, "CPU", 0)
        self.gpu_card = self._create_card(cards_frame, "GPU", 1)
        self.ram_card = self._create_card(cards_frame, "RAM", 2)
        self.disk_card = self._create_card(cards_frame, "Disk", 3)

        # CPU gauge
        self.cpu_canvas, self.cpu_arc, self.cpu_value_label, self.cpu_extra_label = \
            self._create_gauge(self.cpu_card, "CPU Usage")

        # GPU gauge
        self.gpu_canvas, self.gpu_arc, self.gpu_value_label, self.gpu_extra_label = \
            self._create_gauge(self.gpu_card, "GPU Usage", accent=self.neon_blue)

        # RAM gauge
        self.ram_canvas, self.ram_arc, self.ram_value_label, self.ram_extra_label = \
            self._create_gauge(self.ram_card, "RAM Usage", accent=self.neon_purple)

        # Disk card content (bar instead of gauge)
        self.disk_bar = ctk.CTkProgressBar(
            self.disk_card,
            height=18,
            corner_radius=10,
            progress_color=self.neon_blue
        )
        self.disk_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 5))
        self.disk_card.grid_columnconfigure(0, weight=1)

        self.disk_label_main = ctk.CTkLabel(
            self.disk_card,
            text="Disk Usage",
            font=("Segoe UI", 14, "bold"),
            text_color=self.text_main
        )
        self.disk_label_main.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 0), columnspan=2)

        self.disk_label_value = ctk.CTkLabel(
            self.disk_card,
            text="0% (0 / 0 GB)",
            font=("Segoe UI", 12),
            text_color=self.text_muted
        )
        self.disk_label_value.grid(row=2, column=0, sticky="w", padx=20)

        self.disk_label_rw = ctk.CTkLabel(
            self.disk_card,
            text="R/W: 0 / 0 MB/s",
            font=("Segoe UI", 12),
            text_color=self.text_muted
        )
        self.disk_label_rw.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 15))

        # ---- BOTTOM: NETWORK + TEMP + BATTERY + SYSTEM INFO ----

        # Left: Network + temps
        left_bottom = ctk.CTkFrame(bottom_frame, fg_color=self.bg_dark)
        left_bottom.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right: system info
        right_bottom = ctk.CTkFrame(bottom_frame, fg_color=self.bg_dark)
        right_bottom.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Network card
        self.net_card = self._create_info_card(left_bottom, "Network", icon="🌐")
        self.net_label_up = ctk.CTkLabel(
            self.net_card,
            text="Upload: 0.0 KB/s",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.net_label_up.pack(anchor="w", padx=18)

        self.net_label_down = ctk.CTkLabel(
            self.net_card,
            text="Download: 0.0 KB/s",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.net_label_down.pack(anchor="w", padx=18, pady=(0, 8))

        # Temps card
        self.temp_card = self._create_info_card(left_bottom, "Temperatures", icon="🔥")
        self.cpu_temp_label = ctk.CTkLabel(
            self.temp_card,
            text="CPU Temp: N/A",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.cpu_temp_label.pack(anchor="w", padx=18)

        self.gpu_temp_label = ctk.CTkLabel(
            self.temp_card,
            text="GPU Temp: N/A",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.gpu_temp_label.pack(anchor="w", padx=18, pady=(0, 8))

        # Battery card
        self.battery_card = self._create_info_card(right_bottom, "Battery", icon="🔋")
        self.battery_label = ctk.CTkLabel(
            self.battery_card,
            text="Battery: N/A",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.battery_label.pack(anchor="w", padx=18)

        self.battery_extra_label = ctk.CTkLabel(
            self.battery_card,
            text="Status: -",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.battery_extra_label.pack(anchor="w", padx=18, pady=(0, 8))

        # System info card
        self.sysinfo_card = self._create_info_card(right_bottom, "System Info", icon="💻")
        os_name = f"{platform.system()} {platform.release()}"
        self.sysinfo_os_label = ctk.CTkLabel(
            self.sysinfo_card,
            text=f"OS: {os_name}",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.sysinfo_os_label.pack(anchor="w", padx=18)

        self.sysinfo_cpu_label = ctk.CTkLabel(
            self.sysinfo_card,
            text=f"CPU Cores: {psutil.cpu_count(logical=True)}",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.sysinfo_cpu_label.pack(anchor="w", padx=18)

        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
        self.sysinfo_boot_label = ctk.CTkLabel(
            self.sysinfo_card,
            text=f"Boot: {boot_time}",
            font=("Segoe UI", 12),
            text_color=self.text_main
        )
        self.sysinfo_boot_label.pack(anchor="w", padx=18, pady=(0, 8))

    def _create_card(self, parent, title, col_index):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.card_dark,
            corner_radius=18,
            border_width=1,
            border_color=self.card_border
        )
        card.grid(row=0, column=col_index, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col_index, weight=1)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=self.text_main
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(12, 0))
        return card

    def _create_gauge(self, parent, subtitle, accent=None):
        if accent is None:
            accent = self.neon_purple

        canvas = tk.Canvas(
            parent,
            width=160,
            height=160,
            bg=self.card_dark,
            highlightthickness=0
        )
        canvas.grid(row=1, column=0, padx=10, pady=5)

        # track
        canvas.create_oval(
            15, 15, 145, 145,
            outline="#111827",
            width=16
        )
        # arc
        arc = canvas.create_arc(
            15, 15, 145, 145,
            start=90,
            extent=0,
            style="arc",
            outline=accent,
            width=16
        )

        value_label = ctk.CTkLabel(
            parent,
            text="0%",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_main
        )
        value_label.grid(row=2, column=0, pady=(0, 2))

        extra_label = ctk.CTkLabel(
            parent,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color=self.text_muted
        )
        extra_label.grid(row=3, column=0, pady=(0, 12))

        return canvas, arc, value_label, extra_label

    def _create_info_card(self, parent, title, icon="ℹ"):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.card_dark,
            corner_radius=18,
            border_width=1,
            border_color=self.card_border
        )
        card.pack(fill="x", padx=10, pady=8)

        header = ctk.CTkLabel(
            card,
            text=f"{icon}  {title}",
            font=("Segoe UI", 14, "bold"),
            text_color=self.text_main
        )
        header.pack(anchor="w", padx=18, pady=(10, 4))
        return card

    # ================== OVERLAY HUD ==================

    def _create_overlay(self):
        if self.overlay and self.overlay.winfo_exists():
            return

        self.overlay = ctk.CTkToplevel(self)
        self.overlay.title("Performance Overlay")
        self.overlay.geometry("480x70+20+20")
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(fg_color="#020617")
        self.overlay.overrideredirect(False)  # set True for borderless

        container = ctk.CTkFrame(
            self.overlay,
            fg_color="#020617",
            corner_radius=18,
            border_width=1,
            border_color=self.card_border
        )
        container.pack(fill="both", expand=True, padx=5, pady=5)

        font_main = ("Segoe UI", 12, "bold")
        font_sub = ("Segoe UI", 11)

        self.overlay_cpu = ctk.CTkLabel(
            container, text="CPU: --%", font=font_main, text_color=self.neon_purple
        )
        self.overlay_cpu.pack(side="left", padx=10)

        self.overlay_gpu = ctk.CTkLabel(
            container, text="GPU: --%", font=font_main, text_color=self.neon_blue
        )
        self.overlay_gpu.pack(side="left", padx=10)

        self.overlay_ram = ctk.CTkLabel(
            container, text="RAM: --/-- GB", font=font_sub, text_color=self.text_main
        )
        self.overlay_ram.pack(side="left", padx=10)

        self.overlay_net = ctk.CTkLabel(
            container, text="D: 0.0 MB/s · U: 0.0 MB/s", font=font_sub, text_color=self.text_muted
        )
        self.overlay_net.pack(side="left", padx=10)

        # if overlay is closed manually
        self.overlay.protocol("WM_DELETE_WINDOW", self._on_overlay_close)

    def _toggle_overlay(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        else:
            self._create_overlay()

    def _on_overlay_close(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None

    # ================== DATA + UPDATE LOOP ==================

    def _set_gauge(self, canvas, arc_id, percent):
        percent = max(0, min(100, percent))
        extent = - (percent / 100.0) * 360.0
        canvas.itemconfigure(arc_id, extent=extent)

    def update_stats(self):
        # ----- CPU -----
        cpu_percent = psutil.cpu_percent(interval=None)
        self._set_gauge(self.cpu_canvas, self.cpu_arc, cpu_percent)
        self.cpu_value_label.configure(text=f"{cpu_percent:.1f}%")

        # CPU temp (if available)
        cpu_temp = self._get_cpu_temp()
        if cpu_temp is not None:
            self.cpu_extra_label.configure(text=f"CPU Temp: {cpu_temp:.1f}°C")
        else:
            self.cpu_extra_label.configure(text="CPU Temp: N/A")

        # ----- GPU -----
        gpu_percent, gpu_temp, gpu_mem_str = self._get_gpu_info()

        if gpu_percent is not None:
            self._set_gauge(self.gpu_canvas, self.gpu_arc, gpu_percent)
            self.gpu_value_label.configure(text=f"{gpu_percent:.1f}%")
        else:
            self._set_gauge(self.gpu_canvas, self.gpu_arc, 0)
            self.gpu_value_label.configure(text="N/A")

        extra = "GPU: "
        if gpu_temp is not None:
            extra += f"{gpu_temp:.1f}°C  "
        if gpu_mem_str:
            extra += gpu_mem_str
        if extra == "GPU: ":
            extra = "GPU: Not detected"
        self.gpu_extra_label.configure(text=extra)

        # ----- RAM -----
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        self._set_gauge(self.ram_canvas, self.ram_arc, ram_percent)
        used_gb = ram.used / (1024 ** 3)
        total_gb = ram.total / (1024 ** 3)
        self.ram_value_label.configure(text=f"{ram_percent:.1f}%")
        self.ram_extra_label.configure(
            text=f"{used_gb:.1f} / {total_gb:.1f} GB"
        )

        # ----- DISK -----
        try:
            disk = psutil.disk_usage('/')
        except Exception:
            disk = psutil.disk_usage('C:\\')

        disk_percent = disk.percent
        used = disk.used / (1024 ** 3)
        total = disk.total / (1024 ** 3)

        self.disk_bar.set(disk_percent / 100.0)
        self.disk_label_value.configure(
            text=f"{disk_percent:.1f}% ({used:.1f} / {total:.1f} GB)"
        )

        # We don't have per-second disk R/W easily in this simple version;
        # you can extend using psutil.disk_io_counters() deltas.
        self.disk_label_rw.configure(text="R/W: -- / -- MB/s")

        # ----- NETWORK -----
        now = time.time()
        current_net = psutil.net_io_counters()
        delta_t = max(now - self.last_time, 1e-3)

        up_speed = (current_net.bytes_sent - self.last_net.bytes_sent) / delta_t
        down_speed = (current_net.bytes_recv - self.last_net.bytes_recv) / delta_t

        self.last_net = current_net
        self.last_time = now

        up_kb = up_speed / 1024
        down_kb = down_speed / 1024

        self.net_label_up.configure(text=f"Upload: {up_kb:.1f} KB/s")
        self.net_label_down.configure(text=f"Download: {down_kb:.1f} KB/s")

        # ----- TEMPERATURES (GPU) -----
        if gpu_temp is not None:
            self.gpu_temp_label.configure(text=f"GPU Temp: {gpu_temp:.1f}°C")
        else:
            self.gpu_temp_label.configure(text="GPU Temp: N/A")

        if cpu_temp is not None:
            self.cpu_temp_label.configure(text=f"CPU Temp: {cpu_temp:.1f}°C")
        else:
            self.cpu_temp_label.configure(text="CPU Temp: N/A")

        # ----- BATTERY -----
        batt = None
        try:
            batt = psutil.sensors_battery()
        except Exception:
            batt = None

        if batt is None:
            self.battery_label.configure(text="Battery: N/A (Desktop?)")
            self.battery_extra_label.configure(text="Status: -")
        else:
            self.battery_label.configure(text=f"Battery: {batt.percent:.0f}%")
            status = "Charging" if batt.power_plugged else "On battery"
            if batt.secsleft not in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED):
                mins = batt.secsleft // 60
                status += f" · {mins} min left"
            self.battery_extra_label.configure(text=f"Status: {status}")

        # ----- OVERLAY UPDATE -----
        if self.overlay and self.overlay.winfo_exists():
            self.overlay_cpu.configure(text=f"CPU: {cpu_percent:.0f}%")
            if gpu_percent is not None:
                self.overlay_gpu.configure(text=f"GPU: {gpu_percent:.0f}%")
            else:
                self.overlay_gpu.configure(text="GPU: N/A")
            self.overlay_ram.configure(text=f"RAM: {used_gb:.1f}/{total_gb:.1f} GB")
            self.overlay_net.configure(
                text=f"D: {down_kb/1024:.2f} MB/s · U: {up_kb/1024:.2f} MB/s"
            )

        # Schedule next update after 1000 ms
        self.after(1000, self.update_stats)

    def _get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            # Common keys: 'coretemp', 'k10temp', 'cpu-thermal', etc.
            for key in temps:
                if "cpu" in key.lower() or "core" in key.lower():
                    entries = temps[key]
                    if entries:
                        # average of available
                        vals = [e.current for e in entries if e.current is not None]
                        if vals:
                            return sum(vals) / len(vals)
            return None
        except Exception:
            return None

    def _get_gpu_info(self):
        """
        Returns: (gpu_percent, gpu_temp, mem_str)
        gpu_percent, gpu_temp can be None if no GPU.
        mem_str like '3.1 / 8.0 GB'
        """
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None, None, ""
            g = gpus[0]
            gpu_percent = g.load * 100.0
            gpu_temp = getattr(g, "temperature", None)
            mem_used = getattr(g, "memoryUsed", None)
            mem_total = getattr(g, "memoryTotal", None)
            mem_str = ""
            if mem_used is not None and mem_total is not None:
                mem_str = f"{mem_used:.1f} / {mem_total:.1f} GB"
            return gpu_percent, gpu_temp, mem_str
        except Exception:
            return None, None, ""


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
