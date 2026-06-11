import customtkinter as ctk
import tkinter as tk  
from tkinter import ttk, messagebox
import subprocess
import threading
import re
import os
import sys
import webbrowser
from PIL import Image # Explicitly import Pillow for image handling

# --- GLOBAL UI THEME CONFIGURATION ---
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

# --- BULLETPROOF PATH RESOLVER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class WinDepotModern:
    def __init__(self, root):
        self.root = root
        self.root.title("WinDepot App Store")
        self.root.geometry("950x700")
        self.root.minsize(850, 600)
        
        # GARBAGE COLLECTION SHIELD: Store image references here so they don't get deleted
        self.image_cache = [] 
        self.icon_image = None 
        
        self.root.after(200, self.load_favicon)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) 
        
        # --- UI LAYOUT CREATION ---
        self.setup_navigation_bar()
        
        self.content_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_container.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        self.setup_homepage_view()
        self.setup_results_view()
        self.setup_bottom_log()
        
        self.show_homepage()
        self.log("System Status: Operational. Welcome to the WinDepot App Store Dashboard.")
        
    def load_favicon(self):
        """Safely injects the favicon using strong references."""
        icon_path = resource_path("favicon.png")
        if os.path.exists(icon_path):
            try:
                # Save to self.icon_image to prevent garbage collection!
                self.icon_image = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, self.icon_image)
            except Exception as e:
                self.log(f"[SYSTEM] Could not render icon file. Error: {str(e)}")
        else:
            self.log(f"[SYSTEM] Notice: 'favicon.png' missing at path: {icon_path}")

    def setup_navigation_bar(self):
        self.nav_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.nav_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.nav_frame.grid_columnconfigure(3, weight=1) # Shifted expansion column to accommodate new button
        
        self.github_btn = ctk.CTkButton(
            self.nav_frame, text="GitHub Repo", width=100, height=35,
            fg_color="#333333", hover_color="#444444", text_color="white",
            font=ctk.CTkFont(weight="bold"), command=self.open_github_repository
        )
        self.github_btn.grid(row=0, column=0, padx=(15, 5), pady=15)
        
        self.home_btn = ctk.CTkButton(
            self.nav_frame, text="Home", width=70, height=35,
            font=ctk.CTkFont(weight="bold"), command=self.show_homepage
        )
        self.home_btn.grid(row=0, column=1, padx=5, pady=15)

        # --- NEW MODULE: OPEN APP MANAGEMENT COMPANION ---
        self.manage_btn = ctk.CTkButton(
            self.nav_frame, text="Manage App", width=100, height=35,
            fg_color="#2b2b2b", hover_color="#3a3a3a", text_color="#2ecc71",
            border_color="#2ecc71", border_width=1,
            font=ctk.CTkFont(weight="bold"), command=self.open_management_utility
        )
        self.manage_btn.grid(row=0, column=2, padx=5, pady=15)
        
        self.search_entry = ctk.CTkEntry(self.nav_frame, placeholder_text="Type application name to search WinDepot index registry...", height=35)
        self.search_entry.grid(row=0, column=3, padx=10, pady=15, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.start_search())
        
        self.search_btn = ctk.CTkButton(self.nav_frame, text="Search Repository", command=self.start_search, height=35, font=ctk.CTkFont(weight="bold"))
        self.search_btn.grid(row=0, column=4, padx=10, pady=15)
        
        self.install_btn = ctk.CTkButton(self.nav_frame, text="Install Selected", command=self.start_installation, state="disabled", height=35, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.install_btn.grid(row=0, column=5, padx=15, pady=15)

    def open_management_utility(self):
        """Safely resolves pathing and invokes manage_appdepot.py in an isolated child process."""
        target_path = resource_path("manage_appdepot.py")
        if os.path.exists(target_path):
            self.log("[SYSTEM] Spinning up separate execution context thread for Management Dashboard...")
            try:
                # Runs manage_appdepot.py asynchronously using the active environment runtime
                subprocess.Popen([sys.executable, target_path], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            except Exception as e:
                self.log(f"[ERROR] Failed to launch companion subprocess framework: {str(e)}")
                messagebox.showerror("Process Failure", f"Could not open management utility:\n{str(e)}")
        else:
            self.log(f"[ERROR] Subprocess lookup failed. 'manage_appdepot.py' missing at: {target_path}")
            messagebox.showerror("File Error", f"Management script missing!\nEnsure 'manage_appdepot.py' exists in your directory.")

    def setup_homepage_view(self):
        self.home_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.home_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.home_frame.grid_rowconfigure(0, weight=1)
        
        # Build absolute resource destination paths
        ms_path = resource_path(os.path.join("assets", "ms.png"))
        term_path = resource_path(os.path.join("assets", "terminal.png"))
        comm_path = resource_path(os.path.join("assets", "community.png"))
        
        # Column 1
        self.ms_card = ctk.CTkFrame(self.home_frame, fg_color=("#eef2f7", "#252529"), corner_radius=8)
        self.ms_card.grid(row=0, column=0, padx=20, pady=40, sticky="nsew")
        self.render_card_content(self.ms_card, ms_path, "Microsoft Store Source", "Direct app ingestion pipeline powered securely via native WinGet msstore ecosystem backends.")

        # Column 2
        self.term_card = ctk.CTkFrame(self.home_frame, fg_color=("#eef2f7", "#252529"), corner_radius=8)
        self.term_card.grid(row=0, column=1, padx=20, pady=40, sticky="nsew")
        self.render_card_content(self.term_card, term_path, "Windows Package CLI", "Safe automated asynchronous engine bypassing local multi-threading rendering restrictions entirely.")

        # Column 3
        self.comm_card = ctk.CTkFrame(self.home_frame, fg_color=("#eef2f7", "#252529"), corner_radius=8)
        self.comm_card.grid(row=0, column=2, padx=20, pady=40, sticky="nsew")
        self.render_card_content(self.comm_card, comm_path, "Community Repository", "Instant access deployment manifests updated and verified daily by global manifest maintainers.")

    def render_card_content(self, parent_frame, image_path, title_text, description_text):
        parent_frame.grid_columnconfigure(0, weight=1)
        
        if os.path.exists(image_path):
            try:
                # Load via PIL
                pil_img = Image.open(image_path)
                
                # Convert to CTkImage
                ctk_image = ctk.CTkImage(dark_image=pil_img, light_image=pil_img, size=(90, 90))
                
                # IMPORTANT: Append to cache to prevent garbage collection!
                self.image_cache.append(ctk_image)
                
                img_label = ctk.CTkLabel(parent_frame, image=ctk_image, text="")
                img_label.pack(pady=(40, 15))
            except Exception as e:
                self.log(f"[ERROR] Failed to load image {image_path}: {e}")
                fallback_label = ctk.CTkLabel(parent_frame, text="⚠️ Render Error")
                fallback_label.pack(pady=(40, 15))
        else:
            fallback_label = ctk.CTkLabel(parent_frame, text=f"📦 [Missing: {os.path.basename(image_path)}]", font=ctk.CTkFont(slant="italic", size=11))
            fallback_label.pack(pady=(40, 15))
            
        title = ctk.CTkLabel(parent_frame, text=title_text, font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10, padx=15)
        
        desc = ctk.CTkLabel(parent_frame, text=description_text, font=ctk.CTkFont(size=12), wraplength=200, text_color="gray")
        desc.pack(pady=(5, 30), padx=20)

    def setup_results_view(self):
        self.table_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2a2a2a" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
                        foreground="white" if ctk.get_appearance_mode() == "Dark" else "black",
                        rowheight=28,
                        fieldbackground="#2a2a2a" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
                        bordercolor="#3a3a3a",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", 
                        background="#3a3a3a" if ctk.get_appearance_mode() == "Dark" else "#e0e0e0",
                        foreground="white" if ctk.get_appearance_mode() == "Dark" else "black",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)

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

    def setup_bottom_log(self):
        self.log_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.log_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="Terminal Output Log", font=ctk.CTkFont(size=12, weight="bold"))
        self.log_label.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=130, font=("Consolas", 12), text_color="#2ecc71", fg_color="#1e1e1e")
        self.log_text.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        self.log_text.configure(state="disabled")

    def show_homepage(self):
        self.table_frame.grid_remove()
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.install_btn.configure(state="disabled")
        for item in self.tree.get_children():
            self.tree.delete(item)

    def show_results_view(self):
        self.home_frame.grid_remove()
        self.table_frame.grid(row=0, column=0, sticky="nsew")

    def open_github_repository(self):
        url = "https://github.com/andomatthew1234/WinDepot"
        try:
            webbrowser.open_new_tab(url)
            self.log(f"[SYSTEM] Dispatched target outbound link web-hook browser tab to: {url}")
        except Exception as e:
            self.log(f"[ERROR] Outbound link navigation tracking fault encountered: {str(e)}")

    def log(self, message):
        def append():
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
        self.root.after(0, append)

    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Missing", "Please enter a search keyword.")
            return
            
        self.search_btn.configure(state="disabled", text="Searching...")
        self.log(f"[INFO] Initiating Multi-Variant Scan for term: '{query}'...")
        
        self.show_results_view()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        threading.Thread(target=self.execute_search, args=(query,), daemon=True).start()

    def run_single_winget_call(self, search_term):
        try:
            process = subprocess.run(
                ["winget", "search", search_term, "--accept-source-agreements"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding="utf-8",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if process.returncode == 0 or process.returncode == 2316632084:
                return process.stdout
        except Exception:
            pass
        return ""

    def execute_search(self, query):
        try:
            variants = [query]
            if query.lower() != query:
                variants.append(query.lower())
                
            if " " in query:
                for chunk in query.split():
                    if len(chunk) > 2 and chunk not in variants:
                        variants.append(chunk)

            parsed_apps = []
            seen_ids = set()

            for variant in variants:
                raw_output = self.run_single_winget_call(variant)
                if not raw_output:
                    continue

                lines = raw_output.splitlines()
                header_index = -1
                
                for i, line in enumerate(lines):
                    if line.startswith("---") or "------" in line:
                        header_index = i
                        break
                        
                if header_index != -1 and header_index > 0:
                    data_lines = lines[header_index + 1:]
                    for line in data_lines:
                        if not line.strip():
                            continue
                        parts = re.split(r'\s{2,}', line.strip())
                        if len(parts) >= 3:
                            name = parts[0]
                            app_id = parts[1]
                            version = parts[2]
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
        if not apps:
            self.log("[SYSTEM] Lookup complete. 0 applications found across search variant maps.")
        else:
            for app in apps:
                self.tree.insert("", tk.END, values=app)
            self.log(f"[SYSTEM] Clean aggregation resolved. Found {len(apps)} unique package matches.")
        self.reset_search_button()

    def on_item_select(self, event):
        if self.tree.selection():
            self.install_btn.configure(state="normal")
        else:
            self.install_btn.configure(state="disabled")

    def start_installation(self):
        if not self.tree.selection():
            return
            
        selected_item = self.tree.selection()[0]
        app_values = self.tree.item(selected_item, "values")
        app_id = app_values[1]
        app_name = app_values[0]
        
        self.install_btn.configure(state="disabled")
        self.search_btn.configure(state="disabled")
        
        self.log(f"\n[EXECUTION START] Launching silent automated deployment for: {app_name}...")
        threading.Thread(target=self.execute_installation, args=(app_id,), daemon=True).start()

    def execute_installation(self, app_id):
        try:
            cmd = ["winget", "install", app_id, "--accept-source-agreements", "--accept-package-agreements"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.log(f"  > {line.strip()}")
                    
            return_code = process.poll()
            
            if return_code == 0:
                self.log("[SUCCESS] Package installation sequence resolved cleanly.")
            elif return_code == 2316632107:
                self.log("[INFO] Optimization Complete: This application is already installed and up to date!")
            else:
                self.log(f"[WARNING] Installation finished with unexpected return token: {return_code}")
                
        except Exception as e:
            self.log(f"[FAILURE] Thread execution error environment block: {str(e)}")
            
        finally:
            self.root.after(0, lambda: self.search_btn.configure(state="normal"))
            self.root.after(0, self.on_item_select, None)


if __name__ == "__main__":
    root = ctk.CTk()
    app = WinDepotModern(root)
    root.mainloop()