import customtkinter as ctk
import tkinter as tk  
from tkinter import ttk, messagebox
import subprocess
import threading
import re
import os

# --- GLOBAL UI THEME CONFIGURATION ---
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

class WinDepotModern:
    def __init__(self, root):
        self.root = root
        # BRANDING UPDATE: Changed titlebar name to WinDepot App Store
        self.root.title("WinDepot App Store")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # BRANDING UPDATE: Dynamically load and inject favicon.png asset
        self.root.after(200, self.load_favicon)
        
        # Configure grid weight for responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) # Results table section expands
        
        # --- UI LAYOUT CREATION ---
        self.setup_ui()
        self.log("System Status: Operational. Ready to search the WinDepot index repository.")
        
    def load_favicon(self):
        """Safely injects the favicon.png as the native app window & taskbar icon."""
        icon_path = "favicon.png"
        if os.path.exists(icon_path):
            try:
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, img)
            except Exception as e:
                self.log(f"[SYSTEM] Could not render icon file: {str(e)}")
        else:
            self.log("[SYSTEM] Notice: 'favicon.png' asset missing from local directory path.")

    def setup_ui(self):
        """Builds a polished, modern layout using CustomTkinter widgets."""
        
        # 1. TOP FRAME (Search Controls)
        self.search_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.search_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1) # Entry box stretches
        
        self.search_label = ctk.CTkLabel(self.search_frame, text="Search App:", font=ctk.CTkFont(size=13, weight="bold"))
        self.search_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="e.g., vlc, 7zip, git.git...", height=35)
        self.search_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.start_search())
        
        self.search_btn = ctk.CTkButton(self.search_frame, text="Search Repository", command=self.start_search, height=35, font=ctk.CTkFont(weight="bold"))
        self.search_btn.grid(row=0, column=2, padx=10, pady=15)
        
        self.install_btn = ctk.CTkButton(self.search_frame, text="Install Selected", command=self.start_installation, state="disabled", height=35, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.install_btn.grid(row=0, column=3, padx=15, pady=15)
        
        # 2. MIDDLE FRAME (Results Table Container)
        self.table_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.table_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        
        # Configure Treeview styling to fit into modern dark/light mode context smoothly
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
        
        # 3. BOTTOM FRAME (Terminal Log Component)
        self.log_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.log_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="Terminal Output Log", font=ctk.CTkFont(size=12, weight="bold"))
        self.log_label.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=130, font=("Consolas", 12), text_color="#2ecc71", fg_color="#1e1e1e")
        self.log_text.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        self.log_text.configure(state="disabled")

    # --- LOGGING UTILITY ---
    def log(self, message):
        """Appends status sequences into the embedded terminal view safely across threads."""
        def append():
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
        self.root.after(0, append)

    # --- ASYNC SEARCH ---
    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Missing", "Please enter a search keyword.")
            return
            
        self.search_btn.configure(state="disabled", text="Searching...")
        # BRANDING UPDATE: Changed text from WinGet to WinDepot
        self.log(f"[INFO] Scanning WinDepot index registry maps for target query: '{query}'...")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        threading.Thread(target=self.execute_search, args=(query,), daemon=True).start()

    def execute_search(self, query):
        try:
            process = subprocess.run(
                ["winget", "search", query, "--accept-source-agreements"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding="utf-8",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if process.returncode != 0:
                self.log(f"[ERROR] Registry call failed. Code: {process.returncode}")
                if process.stderr:
                    self.log(f"[DETAILS] {process.stderr.strip()}")
                self.root.after(0, self.reset_search_button)
                return

            lines = process.stdout.splitlines()
            parsed_apps = []
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
                        parsed_apps.append((name, app_id, version, source))
            
            self.root.after(0, self.update_tree_results, parsed_apps)
            
        except Exception as e:
            self.log(f"[EXCEPTION] UI Wrapper internal mapping fault: {str(e)}")
            self.root.after(0, self.reset_search_button)

    def reset_search_button(self):
        self.search_btn.configure(state="normal", text="Search Repository")

    def update_tree_results(self, apps):
        if not apps:
            self.log("[SYSTEM] Lookup complete. 0 applications found matching filter parameters.")
        else:
            for app in apps:
                self.tree.insert("", tk.END, values=app)
            self.log(f"[SYSTEM] Populate operations complete. Parsed {len(apps)} entries successfully.")
        self.reset_search_button()

    # --- ASYNC INSTALLATION ---
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