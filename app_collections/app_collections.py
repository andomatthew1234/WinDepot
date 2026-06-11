import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import subprocess
import threading
import urllib.request
import urllib.error

# --- GLOBAL UI THEME CONFIGURATION ---
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

BULK_FILE = resource_path("bulk.json")

class CollectionsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("WinDepot Curated Collections")
        self.root.geometry("750x600")
        self.root.minsize(700, 500)
        
        self.load_parent_theme()
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.setup_header()
        
        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.COLLECTIONS_DATA = {}
        
        # Show a loading label while fetching cloud data
        self.loading_lbl = ctk.CTkLabel(self.container, text="☁️ Fetching live collections from the cloud...", font=ctk.CTkFont(size=14, weight="bold"))
        self.loading_lbl.grid(row=0, column=0)
        
        self.fetch_cloud_collections()

    # --- PREMIUM UX TOAST NOTIFICATIONS ---
    def show_toast(self, title, message, color_theme="#2ecc71"):
        """Slides a non-blocking notification in from the bottom right."""
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

    # --- CLOUD FETCH ENGINE (PATH A) ---
    def fetch_cloud_collections(self):
        # Update this URL to point to your actual GitHub RAW link once you upload it!
        url = "https://raw.githubusercontent.com/andomatthew1234/windepot/main/collections.json"
        
        def worker():
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    self.COLLECTIONS_DATA = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                # If offline or repo is missing, use offline fallback quietly
                self.COLLECTIONS_DATA = self.get_fallback_data()
                
            self.root.after(0, self.build_ui_after_fetch)
            
        threading.Thread(target=worker, daemon=True).start()

    def get_fallback_data(self):
        return {
            "🧑‍💻 Development Hub": {
                "description": "Essential environments, runtimes, and version control tools for modern software development.",
                "apps": [
                    {"name": "Visual Studio Code", "id": "XP9KHM4BK9FZ7Q"},
                    {"name": "Python 3.13", "id": "9PNRBTZXMB4Z"},
                    {"name": "Git", "id": "Git.Git"}
                ]
            },
            "🌐 Internet & Browsers": {
                "description": "Top-tier web navigation clients optimized for speed, privacy, and development.",
                "apps": [
                    {"name": "Google Chrome", "id": "Google.Chrome"},
                    {"name": "Thorium Browser", "id": "Alex313031.Thorium"}
                ]
            },
            "🔨 Core Utilities": {
                "description": "Powerful system modifications and essential lifestyle applications.",
                "apps": [
                    {"name": "Spotify", "id": "9NCBCSZSJRSB"},
                    {"name": "PowerToys Preview", "id": "XP89DCGQ3K6VLD"}
                ]
            }
        }

    def build_ui_after_fetch(self):
        self.loading_lbl.destroy()
        self.setup_grid_view()
        self.setup_detail_view()
        self.show_grid_view()

    def load_parent_theme(self):
        settings_path = resource_path("settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    data = json.load(f)
                    ctk.set_appearance_mode(data.get("theme", "System"))
            except Exception:
                pass

    def setup_header(self):
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.back_btn = ctk.CTkButton(
            self.header_frame, text="← Back to Collections", width=140, height=35,
            fg_color="#333333", hover_color="#444444", font=ctk.CTkFont(weight="bold"),
            command=self.show_grid_view
        )
        self.back_btn.grid(row=0, column=0, sticky="w")
        self.back_btn.grid_remove()
        
        self.title_lbl = ctk.CTkLabel(
            self.header_frame, text="Curated App Collections", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_lbl.grid(row=0, column=1, sticky="e")

    def setup_grid_view(self):
        self.grid_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        
        row_idx, col_idx = 0, 0
        
        for collection_name, data in self.COLLECTIONS_DATA.items():
            card = ctk.CTkFrame(self.grid_frame, corner_radius=12, fg_color=("#eef2f7", "#252529"))
            card.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            
            title = ctk.CTkLabel(card, text=collection_name, font=ctk.CTkFont(size=18, weight="bold"))
            title.pack(pady=(20, 5), padx=15, anchor="w")
            
            desc = ctk.CTkLabel(card, text=data["description"], font=ctk.CTkFont(size=12), text_color="gray", wraplength=280, justify="left")
            desc.pack(pady=(0, 20), padx=15, anchor="w")
            
            btn = ctk.CTkButton(
                card, text="Explore Collection", height=35,
                font=ctk.CTkFont(weight="bold"), 
                command=lambda name=collection_name: self.open_collection(name)
            )
            btn.pack(pady=(0, 20), padx=15, fill="x")
            
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

    def setup_detail_view(self):
        self.detail_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.detail_frame.grid_columnconfigure(0, weight=1)
        self.detail_frame.grid_rowconfigure(1, weight=1)
        
        self.detail_header = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.detail_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.detail_header.grid_columnconfigure(0, weight=1)
        
        self.detail_title = ctk.CTkLabel(self.detail_header, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.detail_title.grid(row=0, column=0, sticky="w")
        
        self.bulk_add_btn = ctk.CTkButton(
            self.detail_header, text="Add All to Bulk Queue", height=35,
            fg_color="#d35400", hover_color="#e67e22", font=ctk.CTkFont(weight="bold"),
            command=self.add_all_to_bulk
        )
        self.bulk_add_btn.grid(row=0, column=1, sticky="e")
        
        self.list_frame = ctk.CTkFrame(self.detail_frame, corner_radius=10)
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        bg_color = "#2a2a2a" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0"
        fg_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        head_bg = "#3a3a3a" if ctk.get_appearance_mode() == "Dark" else "#e0e0e0"
        style.configure("Treeview", background=bg_color, foreground=fg_color, rowheight=35, fieldbackground=bg_color, borderwidth=0, font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background=head_bg, foreground=fg_color, font=("Segoe UI", 11, "bold"), borderwidth=0)

        columns = ("name", "id")
        self.app_tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode="browse")
        self.app_tree.heading("name", text="Application Name")
        self.app_tree.heading("id", text="Package ID")
        self.app_tree.column("name", width=350, anchor=tk.W)
        self.app_tree.column("id", width=300, anchor=tk.W)
        
        self.app_tree.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")
        self.app_tree.bind("<<TreeviewSelect>>", self.on_app_select)
        
        self.action_footer = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.action_footer.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        self.action_footer.grid_columnconfigure(0, weight=1)
        
        self.add_single_btn = ctk.CTkButton(
            self.action_footer, text="+ Add to Bulk List", height=35, state="disabled",
            fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"),
            command=self.add_single_to_bulk
        )
        self.add_single_btn.grid(row=0, column=0, sticky="e", padx=(0, 10))
        
        self.install_now_btn = ctk.CTkButton(
            self.action_footer, text="Install Now", height=35, state="disabled",
            fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"),
            command=self.install_single_app
        )
        self.install_now_btn.grid(row=0, column=1, sticky="e")

    def show_grid_view(self):
        self.detail_frame.grid_remove()
        self.back_btn.grid_remove()
        self.title_lbl.configure(text="Curated App Collections")
        self.grid_frame.grid(row=0, column=0, sticky="nsew")

    def open_collection(self, collection_name):
        self.grid_frame.grid_remove()
        self.current_collection = collection_name
        self.title_lbl.configure(text="Collection Explorer")
        self.detail_title.configure(text=collection_name)
        
        for item in self.app_tree.get_children():
            self.app_tree.delete(item)
            
        apps = self.COLLECTIONS_DATA[collection_name]["apps"]
        for app in apps:
            self.app_tree.insert("", tk.END, values=(app["name"], app["id"]))
            
        self.back_btn.grid()
        self.add_single_btn.configure(state="disabled")
        self.install_now_btn.configure(text="Install Now", state="disabled")
        self.detail_frame.grid(row=0, column=0, sticky="nsew")

    def on_app_select(self, event):
        if self.app_tree.selection():
            self.add_single_btn.configure(state="normal")
            self.install_now_btn.configure(state="normal")
        else:
            self.add_single_btn.configure(state="disabled")
            self.install_now_btn.configure(state="disabled")

    def get_bulk_items(self):
        if not os.path.exists(BULK_FILE): return []
        try:
            with open(BULK_FILE, "r") as f: return json.load(f)
        except Exception: return []

    def save_bulk_items(self, items):
        try:
            with open(BULK_FILE, "w") as f: json.dump(items, f, indent=4)
        except Exception as e:
            self.show_toast("Error", f"Failed to save bulk list: {e}", color_theme="#e74c3c")

    def add_single_to_bulk(self):
        if not self.app_tree.selection(): return
        item = self.app_tree.item(self.app_tree.selection()[0], "values")
        app_name, app_id = item[0], item[1]
        
        items = self.get_bulk_items()
        if any(i["id"] == app_id for i in items):
            self.show_toast("Notice", f"'{app_name}' is already in your queue.", color_theme="#3498db")
        else:
            items.append({"name": app_name, "id": app_id})
            self.save_bulk_items(items)
            self.show_toast("Added to Queue", f"'{app_name}' has been added to the Bulk List.", color_theme="#2ecc71")

    def add_all_to_bulk(self):
        apps = self.COLLECTIONS_DATA[self.current_collection]["apps"]
        items = self.get_bulk_items()
        added_count = 0
        
        for app in apps:
            if not any(i["id"] == app["id"] for i in items):
                items.append({"name": app["name"], "id": app["id"]})
                added_count += 1
                
        if added_count > 0:
            self.save_bulk_items(items)
            self.show_toast("Bulk Added", f"Queued {added_count} apps from this collection.", color_theme="#2ecc71")
        else:
            self.show_toast("Notice", "All apps are already in your queue.", color_theme="#3498db")

    def install_single_app(self):
        if not self.app_tree.selection(): return
        item = self.app_tree.item(self.app_tree.selection()[0], "values")
        app_name, app_id = item[0], item[1]
        
        self.install_now_btn.configure(text="Installing...", state="disabled")
        self.show_toast("Installing", f"Deployment for {app_name} has started.", color_theme="#f39c12")
        
        def worker():
            try:
                cmd = ["winget", "install", app_id, "--accept-source-agreements", "--accept-package-agreements", "--silent"]
                process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                process.wait()
                if process.returncode == 0 or process.returncode == 2316632107:
                    self.root.after(0, lambda: self.show_toast("Success", f"Successfully installed {app_name}!", color_theme="#2ecc71"))
                else:
                    self.root.after(0, lambda: self.show_toast("Warning", f"{app_name} ended with code {process.returncode}.", color_theme="#e67e22"))
            except Exception as e:
                self.root.after(0, lambda err=e: self.show_toast("Error", f"Failed to install: {err}", color_theme="#e74c3c"))
            finally:
                self.root.after(0, lambda: self.install_now_btn.configure(text="Install Now", state="normal"))
                
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    root = ctk.CTk()
    app = CollectionsManager(root)
    root.mainloop()