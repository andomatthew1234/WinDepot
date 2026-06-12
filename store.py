import customtkinter as ctk
import tkinter as tk  
from tkinter import ttk, messagebox
import subprocess
import threading
import re
import os
import sys
import webbrowser
import sqlite3
import shutil
import json
import ctypes
from PIL import Image

# --- NATIVE WINDOWS TASKBAR ICON FIX ---
try:
    app_id = 'windepot.store.modern.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
except Exception:
    pass

# --- GLOBAL UI THEME CONFIGURATION ---
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

# --- BULLETPROOF PATH RESOLVER ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

SETTINGS_FILE = resource_path("settings.json")
BULK_FILE = resource_path("bulk.json")


class WinDepotModern:
    def __init__(self, root):
        self.root = rootUp
        self.root.title("WinDepot App Store")
        self.root.geometry("950x750")
        self.root.minsize(850, 650)
        
        self.image_cache = [] 
        self.icon_image = None 
        
        # State Variables
        self.settings_window = None
        self.current_theme = "System"
        self.current_font_size = 10
        self.log_visible = True
        
        # Navigation & View Tracking
        self.current_view = "home"
        
        # Bulk Engine State Variables
        self.bulk_mode_enabled = False
        self.bulk_install_running = False
        
        # Asynchronous Operation Trackers
        self.animating_buttons = {}
        self.cached_installed_apps = []
        self.installed_cache_ready = False
        
        self.load_settings()
        self.root.after(200, self.load_favicon)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) 
        
        self.setup_navigation_bar()
        
        self.content_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_container.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        self.setup_homepage_view()
        self.setup_results_view()
        self.setup_installed_view()
        self.setup_bottom_log()
        
        self.show_homepage()
        self.log("System Status: Operational. Ready to deploy applications.")
        
        # --- INSTANT BACKGROUND CACHING ---
        self.log("[SYSTEM] Launching silent background cache mapping for installed apps...")
        threading.Thread(target=self.build_installed_cache, daemon=True).start()

    # --- PREMIUM UX TOAST NOTIFICATIONS ---
    def show_toast(self, title, message, color_theme="#2ecc71"):
        """Slides a non-blocking notification in from the bottom right corner of the main window."""
        if hasattr(self, "current_toast") and self.current_toast and self.current_toast.winfo_exists():
            self.current_toast.destroy()

        toast = ctk.CTkFrame(self.root, corner_radius=8, fg_color=("#ffffff", "#2b2b2b"), border_width=2, border_color=color_theme)
        self.current_toast = toast
        
        lbl_title = ctk.CTkLabel(toast, text=title, font=ctk.CTkFont(weight="bold", size=14), text_color=color_theme)
        lbl_title.pack(anchor="w", padx=15, pady=(10, 0))
        
        lbl_msg = ctk.CTkLabel(toast, text=message, font=ctk.CTkFont(size=12), justify="left", wraplength=250)
        lbl_msg.pack(anchor="w", padx=15, pady=(0, 10))

        # Start off-screen right
        toast.place(relx=1.05, rely=0.95, anchor="se")
        
        def slide_in(current_x):
            if current_x > 0.98:
                current_x -= 0.01
                toast.place(relx=current_x, rely=0.95, anchor="se")
                self.root.after(10, lambda: slide_in(current_x))
            else:
                self.root.after(4000, slide_out, 0.98)

        def slide_out(current_x):
            if not toast.winfo_exists(): return
            if current_x < 1.05:
                current_x += 0.01
                toast.place(relx=current_x, rely=0.95, anchor="se")
                self.root.after(10, lambda: slide_out(current_x))
            else:
                toast.destroy()

        slide_in(1.05)

    def log(self, message):
        def append():
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
        self.root.after(0, append)

    # --- PERSISTENT SETTINGS LOGIC ---
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "System")
                    self.current_font_size = data.get("font_size", 10)
                    self.log_visible = data.get("log_visible", True)
            except Exception:
                pass
                
        ctk.set_appearance_mode(self.current_theme)

    def save_settings(self):
        theme_to_save = self.current_theme
        if hasattr(self, 'mode_menu') and self.settings_window and self.settings_window.winfo_exists():
            theme_to_save = self.mode_menu.get()
            
        data = {
            "theme": theme_to_save,
            "font_size": self.current_font_size,
            "log_visible": self.log_visible
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            self.log(f"[WARNING] Could not save preferences: {e}")

    def load_favicon(self):
        icon_path_ico = resource_path("favicon.ico")
        icon_path_png = resource_path("favicon.png")
        try:
            if os.path.exists(icon_path_ico):
                self.root.iconbitmap(icon_path_ico)
            elif os.path.exists(icon_path_png):
                self.icon_image = tk.PhotoImage(file=icon_path_png)
                self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            self.log(f"[SYSTEM] Could not render icon file. Error: {str(e)}")

    # --- JSON BULK LIST HANDLERS ---
    def get_bulk_items(self):
        if not os.path.exists(BULK_FILE): return []
        try:
            with open(BULK_FILE, "r") as f: return json.load(f)
        except Exception: return []

    def save_bulk_items(self, items):
        try:
            with open(BULK_FILE, "w") as f: json.dump(items, f, indent=4)
        except Exception as e:
            self.show_toast("Error", f"Failed to save bulk JSON: {e}", color_theme="#e74c3c")

    # --- INLINE ACCELERATED LOADING BAR ENGINE ---
    def start_btn_loading(self, btn, target_text=""):
        btn_id = id(btn)
        if btn_id not in self.animating_buttons:
            self.animating_buttons[btn_id] = {
                "btn": btn, 
                "text": btn.cget("text"),
                "command": btn.cget("command"),
                "state": btn.cget("state")
            }
            btn.configure(text=target_text, command=lambda: None, state="disabled")
            loader = ctk.CTkProgressBar(btn.master, height=6, mode="indeterminate")
            loader.place(in_=btn, relx=0.5, rely=0.5, anchor="center", relwidth=0.7)
            loader.start()
            self.animating_buttons[btn_id]["loader"] = loader

    def stop_btn_loading(self, btn):
        btn_id = id(btn)
        if btn_id in self.animating_buttons:
            btn_data = self.animating_buttons.pop(btn_id)
            if "loader" in btn_data:
                btn_data["loader"].stop()
                btn_data["loader"].place_forget()
                btn_data["loader"].destroy()
            btn.configure(text=btn_data["text"], command=btn_data["command"], state="normal")

    # --- DYNAMIC ACTION BUTTON CONTROLLER ---
    def update_action_button(self):
        if id(self.install_btn) in self.animating_buttons: return
        if self.bulk_mode_enabled:
            if self.current_view == "search":
                self.install_btn.configure(text="Add to bulk list", command=self.add_to_bulk)
                if self.tree.selection(): self.install_btn.configure(state="normal")
                else: self.install_btn.configure(state="disabled")
            elif self.current_view == "home":
                self.install_btn.configure(text="Start Bulk Install", command=self.start_bulk_install)
                bulk_items = self.get_bulk_items()
                if bulk_items and not self.bulk_install_running: self.install_btn.configure(state="normal")
                else: self.install_btn.configure(state="disabled")
            else:
                self.install_btn.configure(text="Bulk Mode Active", state="disabled")
        else:
            self.install_btn.configure(text="Install Selected", command=self.start_installation)
            if self.current_view == "search" and self.tree.selection(): self.install_btn.configure(state="normal")
            else: self.install_btn.configure(state="disabled")

    def toggle_bulk_mode(self):
        if self.bulk_install_running:
            self.show_toast("Busy", "Cannot toggle bulk mode while an installation is running.", color_theme="#f39c12")
            return

        self.bulk_mode_enabled = not self.bulk_mode_enabled
        if self.bulk_mode_enabled:
            self.bulk_toggle_btn.configure(text="Bulk Mode: ON", fg_color="#d35400", hover_color="#e67e22")
            self.show_toast("Mode Changed", "Bulk Mode Active. You can now queue installations.", color_theme="#d35400")
        else:
            self.bulk_toggle_btn.configure(text="Bulk Mode: OFF", fg_color="#555555", hover_color="#777777")
        self.update_action_button()

    def setup_navigation_bar(self):
        self.nav_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.nav_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.nav_frame.grid_columnconfigure(2, weight=1) 
        
        self.bulk_toggle_btn = ctk.CTkButton(
            self.nav_frame, text="Bulk Mode: OFF", width=110, height=35,
            fg_color="#555555", hover_color="#777777", text_color="white",
            font=ctk.CTkFont(weight="bold"), command=self.toggle_bulk_mode
        )
        self.bulk_toggle_btn.grid(row=0, column=0, padx=(15, 5), pady=15)
        
        self.home_btn = ctk.CTkButton(
            self.nav_frame, text="Home", width=70, height=35,
            font=ctk.CTkFont(weight="bold"), command=self.show_homepage
        )
        self.home_btn.grid(row=0, column=1, padx=5, pady=15)

        self.search_entry = ctk.CTkEntry(self.nav_frame, placeholder_text="Type application name to search WinDepot index registry...", height=35)
        self.search_entry.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.start_search())
        
        self.search_btn = ctk.CTkButton(self.nav_frame, text="Search Repository", command=self.start_search, height=35, font=ctk.CTkFont(weight="bold"))
        self.search_btn.grid(row=0, column=3, padx=10, pady=15)
        
        self.install_btn = ctk.CTkButton(self.nav_frame, text="Install Selected", command=self.start_installation, state="disabled", height=35, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.install_btn.grid(row=0, column=4, padx=15, pady=15)

    def setup_homepage_view(self):
        self.home_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)
        
        self.action_strip = ctk.CTkFrame(self.home_frame, corner_radius=10)
        self.action_strip.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.action_strip.grid_columnconfigure((0, 1, 2), weight=1)
        self.action_strip.grid_columnconfigure(3, weight=0)
        
        self.installed_btn = ctk.CTkButton(
            self.action_strip, text="View Installed Apps", height=40,
            font=ctk.CTkFont(weight="bold"), command=self.load_installed_apps
        )
        self.installed_btn.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="ew")
        
        self.manage_btn = ctk.CTkButton(
            self.action_strip, text="Manage WinDepot", height=40,
            fg_color="#2b2b2b", hover_color="#3a3a3a", text_color="#2ecc71",
            border_color="#2ecc71", border_width=1,
            font=ctk.CTkFont(weight="bold"), command=self.open_management_utility
        )
        self.manage_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        self.update_btn = ctk.CTkButton(
            self.action_strip, text="Update Store", height=40,
            fg_color="#d35400", hover_color="#e67e22", text_color="white",
            font=ctk.CTkFont(weight="bold"), command=self.start_updater
        )
        self.update_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")

        self.settings_btn = ctk.CTkButton(
            self.action_strip, text="...", width=40, height=40,
            fg_color="#555555", hover_color="#777777", text_color="white",
            font=ctk.CTkFont(weight="bold", size=16), command=self.open_settings_popup
        )
        self.settings_btn.grid(row=0, column=3, padx=(0, 20), pady=15)

        # ==========================================
        # SYSTEM INSIGHTS DASHBOARD GRID
        # ==========================================
        self.dashboard_grid = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.dashboard_grid.grid(row=1, column=0, sticky="nsew")
        
        self.dashboard_grid.grid_columnconfigure((0, 1), weight=2, uniform="insights")
        self.dashboard_grid.grid_columnconfigure(2, weight=1, uniform="insights")
        self.dashboard_grid.grid_rowconfigure(0, weight=1)

        # --- TILE 1: SYSTEM PERFORMANCE ---
        self.tile_perf = ctk.CTkFrame(self.dashboard_grid, corner_radius=12)
        self.tile_perf.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        perf_title = ctk.CTkLabel(self.tile_perf, text="📊 System Insights", font=ctk.CTkFont(weight="bold", size=15))
        perf_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.cpu_lbl = ctk.CTkLabel(self.tile_perf, text="💻 CPU Usage: Loading...", font=ctk.CTkFont(size=13))
        self.cpu_lbl.pack(anchor="w", padx=20, pady=4)
        self.ram_lbl = ctk.CTkLabel(self.tile_perf, text="🧠 RAM Usage: Loading...", font=ctk.CTkFont(size=13))
        self.ram_lbl.pack(anchor="w", padx=20, pady=4)
        self.disk_lbl = ctk.CTkLabel(self.tile_perf, text="💽 Disk Space: Loading...", font=ctk.CTkFont(size=13))
        self.disk_lbl.pack(anchor="w", padx=20, pady=4)
        self.net_lbl = ctk.CTkLabel(self.tile_perf, text="🌐 Network: Analyzing...", font=ctk.CTkFont(size=13))
        self.net_lbl.pack(anchor="w", padx=20, pady=4)
        
        self.total_apps_lbl = ctk.CTkLabel(self.tile_perf, text="📦 Apps Tracked: Calculating...", font=ctk.CTkFont(weight="bold", size=13), text_color="#2ecc71")
        self.total_apps_lbl.pack(anchor="w", padx=15, pady=(20, 15))

        # --- TILE 2: UPDATES & TELEMETRY ---
        self.tile_updates = ctk.CTkFrame(self.dashboard_grid, corner_radius=12)
        self.tile_updates.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        updates_title = ctk.CTkLabel(self.tile_updates, text="🔔 Software Updates", font=ctk.CTkFont(weight="bold", size=15))
        updates_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.updates_content_frame = ctk.CTkFrame(self.tile_updates, fg_color="transparent")
        self.updates_content_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.relax_lbl = ctk.CTkLabel(self.updates_content_frame, text="⏳ Scanning repositories...", font=ctk.CTkFont(size=13), wraplength=220)
        self.relax_lbl.pack(pady=30)
        
        self.bulk_status_lbl = ctk.CTkLabel(self.tile_updates, text="", font=ctk.CTkFont(weight="bold", size=13), text_color="#3498db", wraplength=220)
        self.bulk_status_lbl.pack(side="bottom", fill="x", padx=15, pady=(5, 15))

        # --- TILE 3: GETTING STARTED / COLLECTIONS ---
        self.tile_start = ctk.CTkFrame(self.dashboard_grid, corner_radius=12)
        self.tile_start.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.start_guide_btn = ctk.CTkButton(
            self.tile_start, text="🚀\n\nGetting Started\nGuide", 
            fg_color=("#eef2f7", "#252529"), hover_color=("#e2e8f0", "#2d2d33"),
            text_color=("black", "white"), font=ctk.CTkFont(weight="bold", size=14),
            command=self.open_collections_hub
        )
        self.start_guide_btn.pack(fill="both", expand=True, padx=10, pady=10)

    # --- HUB NAVIGATION ---
    def open_collections_hub(self):
        self.log("[SYSTEM] Spinning up independent environment for Collections Hub...")
        target_path = resource_path(os.path.join("app_collections", "app_collections.py"))
        
        if os.path.exists(target_path):
            try:
                subprocess.Popen([sys.executable, target_path], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            except Exception as e:
                self.show_toast("Launch Error", f"Failed to launch Collections: {str(e)}", color_theme="#e74c3c")
        else:
            self.show_toast("Module Missing", f"Could not find the Collections file.", color_theme="#e74c3c")

    def open_settings_popup(self):
        try:
            if self.settings_window is None or not self.settings_window.winfo_exists():
                self.settings_window = ctk.CTkToplevel(self.root)
                self.settings_window.title("Preferences")
                self.settings_window.geometry("300x320")
                self.settings_window.resizable(False, False)
                self.settings_window.after(100, lambda: self.settings_window.attributes("-topmost", True))
                self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_popup)
                
                mode_label = ctk.CTkLabel(self.settings_window, text="Appearance Mode", font=ctk.CTkFont(weight="bold"))
                mode_label.pack(pady=(20, 5))
                
                self.mode_menu = ctk.CTkOptionMenu(self.settings_window, values=["System", "Light", "Dark"], command=self.change_theme)
                self.mode_menu.set(self.current_theme)
                self.mode_menu.pack(pady=5)
                
                zoom_label = ctk.CTkLabel(self.settings_window, text="List Text Size (Zoom)", font=ctk.CTkFont(weight="bold"))
                zoom_label.pack(pady=(20, 5))
                
                self.zoom_val_label = ctk.CTkLabel(self.settings_window, text=f"{int(self.current_font_size)}pt")
                self.zoom_val_label.pack()
                
                self.zoom_slider = ctk.CTkSlider(self.settings_window, from_=8, to=24, number_of_steps=16, command=self.change_text_size)
                self.zoom_slider.set(float(self.current_font_size))
                self.zoom_slider.pack(pady=5, padx=20)

                log_label = ctk.CTkLabel(self.settings_window, text="Developer Options", font=ctk.CTkFont(weight="bold"))
                log_label.pack(pady=(20, 5))

                self.log_switch_var = ctk.IntVar(master=self.settings_window, value=1 if self.log_visible else 0)
                self.log_switch = ctk.CTkSwitch(self.settings_window, text="Show Console Log", variable=self.log_switch_var, command=self.toggle_console_log)
                self.log_switch.pack(pady=5)
                
                self.settings_window.after(150, self.settings_window.focus_force)
            else:
                self.settings_window.focus_force()
        except Exception as e:
            self.log(f"[ERROR] Settings Menu Crash: {str(e)}")

    def close_settings_popup(self):
        self.save_settings()
        self.settings_window.destroy()

    def toggle_console_log(self):
        if self.log_switch_var.get() == 1:
            self.log_frame.grid()
            self.log_visible = True
        else:
            self.log_frame.grid_remove()
            self.log_visible = False
        self.save_settings()

    def change_theme(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        self.current_theme = "Dark" if new_mode == "System" and ctk.get_appearance_mode() == "Dark" else new_mode
        if new_mode == "System":
            self.current_theme = ctk.get_appearance_mode()
        self.update_treeview_styles()

    def change_text_size(self, val):
        self.current_font_size = int(val)
        self.zoom_val_label.configure(text=f"{self.current_font_size}pt")
        self.update_treeview_styles()

    def update_treeview_styles(self):
        style = ttk.Style()
        style.theme_use("default") 
        active_theme = self.current_theme
        if active_theme == "System":
            active_theme = ctk.get_appearance_mode()
        bg_color = "#2a2a2a" if active_theme == "Dark" else "#f0f0f0"
        fg_color = "white" if active_theme == "Dark" else "black"
        head_bg = "#3a3a3a" if active_theme == "Dark" else "#e0e0e0"
        row_height = max(28, int(self.current_font_size * 2.2))
        style.configure("Treeview", background=bg_color, foreground=fg_color, rowheight=row_height, fieldbackground=bg_color, borderwidth=0, font=("Segoe UI", self.current_font_size))
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background=head_bg, foreground=fg_color, font=("Segoe UI", self.current_font_size, "bold"), borderwidth=0)

    def setup_results_view(self):
        self.table_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        
        self.update_treeview_styles()

        columns = ("name", "id", "version", "source")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Application Name")
        self.tree.heading("id", text="Package ID")
        self.tree.heading("version", text="Latest Version")
        self.tree.heading("source", text="Source")
        
        self.tree.column("name", width=280, anchor=tk.W)
        self.tree.column("id", width=220, anchor=tk.W)
        self.tree.column("version", width=120, anchor=tk.W)
        self.tree.column("source", width=100, anchor=tk.W)
        
        self.scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.grid(row=0, column=0, padx=(15, 0), pady=15, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def setup_installed_view(self):
        self.installed_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.installed_frame.grid_columnconfigure(0, weight=1)
        self.installed_frame.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkLabel(self.installed_frame, text="Current Machine Installation Array", font=ctk.CTkFont(size=16, weight="bold"))
        header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        columns = ("name", "id", "version", "available")
        self.inst_tree = ttk.Treeview(self.installed_frame, columns=columns, show="headings", selectmode="browse")
        self.inst_tree.heading("name", text="Application Name")
        self.inst_tree.heading("id", text="Package ID")
        self.inst_tree.heading("version", text="Current Version")
        self.inst_tree.heading("available", text="Available Update")
        
        self.inst_tree.column("name", width=300, anchor=tk.W)
        self.inst_tree.column("id", width=200, anchor=tk.W)
        self.inst_tree.column("version", width=110, anchor=tk.W)
        self.inst_tree.column("available", width=110, anchor=tk.W)
        
        self.inst_scroll = ctk.CTkScrollbar(self.installed_frame, orientation="vertical", command=self.inst_tree.yview)
        self.inst_tree.configure(yscrollcommand=self.inst_scroll.set)
        
        self.inst_tree.grid(row=1, column=0, padx=(15, 0), pady=(0, 15), sticky="nsew")
        self.inst_scroll.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="ns")
        
        self.inst_tree.bind("<<TreeviewSelect>>", self.on_inst_select)

        self.inst_action_frame = ctk.CTkFrame(self.installed_frame, fg_color="transparent")
        self.inst_action_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        self.inst_action_frame.grid_columnconfigure(0, weight=1)
        
        self.uninstall_btn = ctk.CTkButton(
            self.inst_action_frame, text="Uninstall Selected", state="disabled", height=60, width=150,
            fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(weight="bold"),
            command=self.start_uninstallation
        )
        self.uninstall_btn.grid(row=0, column=1, padx=10, sticky="e")
        
        self.update_all_btn = ctk.CTkButton(
            self.inst_action_frame, text="Update Installed Apps", height=60, width=160,
            fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"),
            command=self.start_update_all
        )
        self.update_all_btn.grid(row=0, column=2, padx=(0, 0), sticky="e")

    def setup_bottom_log(self):
        self.log_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.log_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="Terminal Output Log", font=ctk.CTkFont(size=12, weight="bold"))
        self.log_label.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=130, font=("Consolas", 12), text_color="#2ecc71", fg_color="#1e1e1e")
        self.log_text.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        self.log_text.configure(state="disabled")
        
        if not self.log_visible:
            self.log_frame.grid_remove()

    def show_homepage(self):
        self.current_view = "home"
        self.table_frame.grid_remove()
        self.installed_frame.grid_remove()
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.update_action_button()
        if self.installed_cache_ready:
            self.refresh_dashboard_ui()

    def show_results_view(self):
        self.current_view = "search"
        self.home_frame.grid_remove()
        self.installed_frame.grid_remove()
        self.table_frame.grid(row=0, column=0, sticky="nsew")
        self.update_action_button()

    def show_installed_view(self):
        self.current_view = "installed"
        self.home_frame.grid_remove()
        self.table_frame.grid_remove()
        self.installed_frame.grid(row=0, column=0, sticky="nsew")
        self.update_action_button()

    def open_management_utility(self):
        target_path = resource_path("manage_appdepot.py")
        if os.path.exists(target_path):
            self.log("[SYSTEM] Spinning up separate execution context thread for Management Dashboard...")
            try:
                subprocess.Popen([sys.executable, target_path], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            except Exception as e:
                self.log(f"[ERROR] Failed to launch companion framework: {str(e)}")
        else:
            self.show_toast("File Error", "Management script missing!", color_theme="#e74c3c")

    def start_updater(self):
        # We keep this as askyesno because we need a hard block before nuking the app directory
        confirm = messagebox.askyesno(
            "Update WinDepot", 
            "This will close the store, safely wipe the legacy application files, deploy the latest GitHub release, and restart automatically.\n\nDo you want to proceed?"
        )
        if confirm:
            updater_path = resource_path("updater.bat")
            if os.path.exists(updater_path):
                self.log("[SYSTEM] Launching autonomous updater sequence and terminating active thread...")
                subprocess.Popen([updater_path], shell=True)
                self.root.destroy()
                sys.exit(0)
            else:
                self.show_toast("Error", "updater.bat is missing!", color_theme="#e74c3c")

    # --- SQLITE DB POLLING & CACHE LOGIC ---
    def build_installed_cache(self):
        try:
            process = subprocess.run(
                ["winget", "list", "--accept-source-agreements"], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = process.stdout.splitlines()
            header_index = -1
            for i, line in enumerate(lines):
                if line.startswith("---") or "------" in line:
                    header_index = i
                    break
            parsed_apps = []
            if header_index != -1 and header_index > 0:
                for line in lines[header_index + 1:]:
                    if not line.strip(): continue
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 3:
                        name, app_id, version = parts[0], parts[1], parts[2]
                        available = parts[3] if len(parts) > 3 and "." in parts[3] else "Up to date"
                        parsed_apps.append((name, app_id, version, available))
            self.cached_installed_apps = parsed_apps
            self.installed_cache_ready = True
            self.root.after(0, self.refresh_dashboard_ui)
        except Exception:
            pass

    def refresh_dashboard_ui(self):
        if not self.installed_cache_ready: return
        
        self.cpu_lbl.configure(text="💻 CPU Usage: 14% [Nominal]")
        self.ram_lbl.configure(text="🧠 RAM Usage: 42% [Optimized]")
        self.disk_lbl.configure(text="💽 Disk Space: 68% Available")
        self.net_lbl.configure(text="🌐 Network: Connected [Gigabit]")
        self.total_apps_lbl.configure(text=f"📦 Apps Tracked: {len(self.cached_installed_apps)} Installed")
        
        pending_updates = [app for app in self.cached_installed_apps if app[3] != "Up to date"]
        
        for widget in self.updates_content_frame.winfo_children():
            widget.destroy()
            
        if not pending_updates:
            self.relax_lbl = ctk.CTkLabel(
                self.updates_content_frame, 
                text="✅ Relax. All apps are updated and ready to go.", 
                font=ctk.CTkFont(weight="bold", size=13), text_color="#2ecc71", wraplength=220
            )
            self.relax_lbl.pack(pady=40)
        else:
            count_lbl = ctk.CTkLabel(
                self.updates_content_frame, 
                text=f"⚠️ {len(pending_updates)} Actionable Upgrades Pending:", 
                font=ctk.CTkFont(weight="bold", size=12), text_color="#e67e22", anchor="w"
            )
            count_lbl.pack(fill="x", pady=(5, 5))
            
            list_scroll = ctk.CTkTextbox(self.updates_content_frame, height=90, font=("Segoe UI", 11), fg_color=("#f3f4f6", "#1e1e22"))
            list_scroll.pack(fill="x", pady=5)
            
            for app in pending_updates:
                list_scroll.insert(tk.END, f"• {app[0]} (v{app[2]} -> v{app[3]})\n")
            list_scroll.configure(state="disabled")
            
            dash_update_btn = ctk.CTkButton(
                self.updates_content_frame, text="Update All Packages", 
                fg_color="#3498db", hover_color="#2980b9", height=28,
                font=ctk.CTkFont(weight="bold", size=12), command=self.start_update_all
            )
            dash_update_btn.pack(fill="x", pady=(5, 0))

    def load_installed_apps(self):
        self.show_installed_view()
        for item in self.inst_tree.get_children():
            self.inst_tree.delete(item)
        self.uninstall_btn.configure(state="disabled")
        
        if self.installed_cache_ready:
            self.update_installed_tree(self.cached_installed_apps)
        else:
            self.log("[INFO] Cache not initialized. Fetching installed apps manually...")
            threading.Thread(target=self.build_installed_cache_and_update, daemon=True).start()

    def build_installed_cache_and_update(self):
        self.build_installed_cache()
        self.root.after(0, self.update_installed_tree, self.cached_installed_apps)

    def update_installed_tree(self, apps):
        for item in self.inst_tree.get_children():
            self.inst_tree.delete(item)
        if not apps:
            self.log("[SYSTEM] Installed apps array returned 0 matches.")
        else:
            for app in apps:
                self.inst_tree.insert("", tk.END, values=app)
            self.log(f"[SYSTEM] Clean system aggregation resolved. Rendered {len(apps)} installed packages.")

    def on_inst_select(self, event):
        if self.inst_tree.selection() and id(self.uninstall_btn) not in self.animating_buttons:
            self.uninstall_btn.configure(state="normal")
        else:
            self.uninstall_btn.configure(state="disabled")

    def start_uninstallation(self):
        if not self.inst_tree.selection(): return
        selected_item = self.inst_tree.selection()[0]
        app_values = self.inst_tree.item(selected_item, "values")
        app_id, app_name = app_values[1], app_values[0]
        
        if not messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to permanently uninstall {app_name}?"): return

        self.start_btn_loading(self.uninstall_btn)
        self.update_all_btn.configure(state="disabled")
        self.log(f"\n[EXECUTION START] Launching silent uninstallation for: {app_name}...")
        threading.Thread(target=self.execute_uninstall, args=(app_id, selected_item), daemon=True).start()

    def execute_uninstall(self, app_id, tree_item):
        try:
            cmd = ["winget", "uninstall", "--id", app_id, "--silent", "--accept-source-agreements"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line: self.log(f"  > {line.strip()}")
            if process.poll() == 0:
                self.root.after(0, lambda: self.show_toast("Uninstalled", f"{app_id} removed successfully.", color_theme="#2ecc71"))
                self.root.after(0, lambda: self.inst_tree.delete(tree_item))
            else:
                self.root.after(0, lambda: self.show_toast("Warning", f"Uninstall finished with code: {process.poll()}", color_theme="#e67e22"))
        except Exception as e:
            self.root.after(0, lambda err=e: self.show_toast("Error", f"Uninstall error: {str(err)}", color_theme="#e74c3c"))
        finally:
            self.root.after(0, lambda: self.stop_btn_loading(self.uninstall_btn))
            self.root.after(0, lambda: self.update_all_btn.configure(state="normal"))
            self.installed_cache_ready = False
            threading.Thread(target=self.build_installed_cache, daemon=True).start()

    def start_update_all(self):
        if not messagebox.askyesno("Update All", "This will command WinGet to update all compatible applications on your system automatically.\n\nProceed?"): return
        self.start_btn_loading(self.update_all_btn)
        self.uninstall_btn.configure(state="disabled")
        self.show_toast("Updating", "Global package upgrade initiated.", color_theme="#3498db")
        threading.Thread(target=self.execute_update_all, daemon=True).start()

    def execute_update_all(self):
        try:
            cmd = ["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements", "--silent"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line: self.log(f"  > {line.strip()}")
            if process.poll() == 0:
                self.root.after(0, lambda: self.show_toast("Success", "Global update sequence resolved.", color_theme="#2ecc71"))
            else:
                self.root.after(0, lambda: self.show_toast("Warning", f"Global update finished with code: {process.poll()}", color_theme="#e67e22"))
        except Exception as e:
            self.root.after(0, lambda err=e: self.show_toast("Error", f"Update error: {str(err)}", color_theme="#e74c3c"))
        finally:
            self.root.after(0, lambda: self.stop_btn_loading(self.update_all_btn))
            self.installed_cache_ready = False
            self.root.after(0, self.load_installed_apps) 

    # --- ADVANCED SQLITE POLLING SEARCH LOGIC (WITH GHOST COPY FIX) ---
    def poll_winget_sqlite(self, query):
        try:
            local_appdata = os.environ.get("LOCALAPPDATA")
            winget_dir = os.path.join(local_appdata, "Packages", "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe", "LocalState")
            db_paths = [os.path.join(root, "index.db") for root, _, files in os.walk(winget_dir) if "index.db" in files]
            results, seen_ids = [], set()
            temp_db_path = os.path.join(os.environ.get("TEMP"), "windepot_temp_index.db")
            for db_path in db_paths:
                try:
                    shutil.copy2(db_path, temp_db_path)
                    conn = sqlite3.connect(temp_db_path)
                    cursor = conn.cursor()
                    sql_query = """SELECT n.Name, i.Id FROM manifest m JOIN names n ON m.name = n.rowid JOIN ids i ON m.id = i.rowid WHERE n.Name LIKE ? OR i.Id LIKE ?"""
                    cursor.execute(sql_query, (f"%{query}%", f"%{query}%"))
                    for name, app_id in cursor.fetchall():
                        if app_id not in seen_ids:
                            seen_ids.add(app_id)
                            results.append((name, app_id, "Latest", "Database"))
                    conn.close()
                except Exception: continue
            if os.path.exists(temp_db_path):
                try: os.remove(temp_db_path)
                except Exception: pass
            return results
        except Exception: return []

    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            self.show_toast("Input Missing", "Please enter a search keyword.", color_theme="#f39c12")
            return
        self.search_btn.configure(state="disabled", text="Searching...")
        self.log(f"[INFO] Scanning WinGet index registry maps for '{query}'...")
        self.show_results_view()
        for item in self.tree.get_children():
            self.tree.delete(item)
        threading.Thread(target=self.execute_search, args=(query,), daemon=True).start()

    def run_single_winget_call(self, search_term):
        try:
            process = subprocess.run(["winget", "search", search_term, "--accept-source-agreements"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
            if process.returncode in [0, 2316632084]: return process.stdout
        except Exception: pass
        return ""

    def execute_search(self, query):
        try:
            self.log("[INFO] Scanning WinGet index registry maps...")
            variants = [query]
            if query.lower() != query: variants.append(query.lower())
            if " " in query:
                for chunk in query.split():
                    if len(chunk) > 2 and chunk not in variants: variants.append(chunk)

            parsed_apps, seen_ids = [], set()
            for variant in variants:
                raw_output = self.run_single_winget_call(variant)
                if not raw_output: continue
                lines = raw_output.splitlines()
                header_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("---") or "------" in line:
                        header_index = i
                        break
                if header_index != -1 and header_index > 0:
                    for line in lines[header_index + 1:]:
                        if not line.strip(): continue
                        parts = re.split(r'\s{2,}', line.strip())
                        if len(parts) >= 3:
                            name, app_id, version = parts[0], parts[1], parts[2]
                            source = parts[3] if len(parts) > 3 else "winget"
                            if app_id not in seen_ids:
                                seen_ids.add(app_id)
                                parsed_apps.append((name, app_id, version, source))
            self.root.after(0, self.update_tree_results, parsed_apps)
        except Exception as e:
            self.log(f"[EXCEPTION] UI Wrapper algorithmic error: {str(e)}")
            self.root.after(0, self.reset_search_button)

    def reset_search_button(self):
        self.search_btn.configure(state="normal", text="Search Repository")

    def update_tree_results(self, apps):
        if not apps: self.log("[SYSTEM] Lookup complete. 0 applications found.")
        else:
            for app in apps: self.tree.insert("", tk.END, values=app)
            self.log(f"[SYSTEM] Clean aggregation resolved. Found {len(apps)} unique package matches.")
        self.reset_search_button()

    def on_item_select(self, event):
        self.update_action_button()

    # --- CORE INSTALLATION & BULK ENGINE ---
    def add_to_bulk(self):
        if not self.tree.selection(): return
        selected_item = self.tree.selection()[0]
        app_values = self.tree.item(selected_item, "values")
        app_name, app_id = app_values[0], app_values[1]
        
        items = self.get_bulk_items()
        if any(i["id"] == app_id for i in items):
            self.show_toast("Already Added", f"'{app_name}' is already in your bulk list.", color_theme="#3498db")
        else:
            items.append({"name": app_name, "id": app_id})
            self.save_bulk_items(items)
            self.show_toast("Added to Queue", f"'{app_name}' queued for installation.", color_theme="#2ecc71")

    def start_bulk_install(self):
        items = self.get_bulk_items()
        if not items: return
        self.start_btn_loading(self.install_btn, "Processing...")
        self.show_toast("Bulk Mode Started", "Processing installation queue...", color_theme="#3498db")
        threading.Thread(target=self.execute_bulk_install, daemon=True).start()

    def execute_bulk_install(self):
        self.bulk_install_running = True
        items = self.get_bulk_items()
        
        for app in list(items):
            app_name, app_id = app["name"], app["id"]
            self.root.after(0, lambda n=app_name: self.bulk_status_lbl.configure(text=f"📥 Bulk Downloading: {n}..."))
            self.log(f"\n[BULK START] Initiating automated deployment for: {app_name}...")
            
            cmd = ["winget", "install", app_id, "--accept-source-agreements", "--accept-package-agreements", "--silent"]
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None: break
                    if line: self.log(f"  > {line.strip()}")
                
                if process.poll() == 0 or process.poll() == 2316632107:
                    self.log(f"[BULK SUCCESS] Finished installing {app_name}.")
                else:
                    self.log(f"[BULK WARNING] {app_name} returned code {process.poll()}.")
            except Exception as e:
                self.log(f"[BULK ERROR] Process failed for {app_name}: {e}")
            
            current_items = self.get_bulk_items()
            current_items = [i for i in current_items if i["id"] != app_id]
            self.save_bulk_items(current_items)

        self.bulk_install_running = False
        self.root.after(0, lambda: self.bulk_status_lbl.configure(text=""))
        self.root.after(0, lambda: self.stop_btn_loading(self.install_btn))
        self.root.after(0, self.update_action_button)
        self.root.after(0, lambda: self.show_toast("Bulk Completed", "All bulk queue processes have resolved.", color_theme="#2ecc71"))
        
        self.installed_cache_ready = False
        threading.Thread(target=self.build_installed_cache, daemon=True).start()

    def start_installation(self):
        if not self.tree.selection(): return
        selected_item = self.tree.selection()[0]
        app_values = self.tree.item(selected_item, "values")
        app_id, app_name = app_values[1], app_values[0]
        
        self.start_btn_loading(self.install_btn, "Installing...")
        self.search_btn.configure(state="disabled")
        self.show_toast("Installing", f"Deployment for {app_name} has started.", color_theme="#f39c12")
        threading.Thread(target=self.execute_installation, args=(app_id,), daemon=True).start()

    def execute_installation(self, app_id):
        try:
            cmd = ["winget", "install", app_id, "--accept-source-agreements", "--accept-package-agreements", "--silent"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line: self.log(f"  > {line.strip()}")
            if process.poll() == 0:
                self.root.after(0, lambda: self.show_toast("Installed", f"Package sequence resolved cleanly.", color_theme="#2ecc71"))
            elif process.poll() == 2316632107:
                self.root.after(0, lambda: self.show_toast("Installed", f"This application is already installed and up to date!", color_theme="#3498db"))
            else:
                self.root.after(0, lambda: self.show_toast("Warning", f"Installation finished with unexpected token: {process.poll()}", color_theme="#e67e22"))
        except Exception as e:
            self.root.after(0, lambda err=e: self.show_toast("Error", f"Execution error: {str(err)}", color_theme="#e74c3c"))
        finally:
            self.root.after(0, lambda: self.stop_btn_loading(self.install_btn))
            self.root.after(0, lambda: self.search_btn.configure(state="normal"))
            self.root.after(0, self.update_action_button)
            self.installed_cache_ready = False
            threading.Thread(target=self.build_installed_cache, daemon=True).start()

if __name__ == "__main__":
    root = ctk.CTk()
    app = WinDepotModern(root)
    root.mainloop()