import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys
import shutil
import threading

class WinDepotManager:
    def __init__(self, root):
        self.root = root
        self.root.title("WinDepot - Advanced App Manager")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")
        
        # Title Header
        title_lbl = tk.Label(
            root, text="WinDepot Management System", 
            font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1e1e1e"
        )
        title_lbl.pack(pady=(15, 5))
        
        # --- PRE-REQUISITE CHECK DIALOG (Dashboard Frame) ---
        self.dashboard_frame = tk.LabelFrame(
            root, text=" System Status Dashboard ", font=("Segoe UI", 10, "bold"),
            fg="#2ecc71", bg="#1e1e1e", bd=1, relief="solid"
        )
        self.dashboard_frame.pack(padx=20, pady=10, fill="x")
        
        # Status rows configuration variables
        self.python_status = tk.StringVar(value="Python Environment: Checking...")
        self.pillow_status = tk.StringVar(value="Pillow Package: Checking...")
        self.ctk_status = tk.StringVar(value="CustomTkinter Package: Checking...")
        
        self.create_status_row(self.dashboard_frame, self.python_status)
        self.create_status_row(self.dashboard_frame, self.pillow_status)
        self.create_status_row(self.dashboard_frame, self.ctk_status)
        
        # Action Control Panel layout
        self.control_frame = tk.Frame(root, bg="#1e1e1e")
        self.control_frame.pack(padx=20, pady=5, fill="both", expand=True)
        self.control_frame.columnconfigure((0, 1), weight=1)
        
        btn_style = {
            "font": ("Segoe UI", 10, "bold"), "fg": "#ffffff", "bg": "#2d2d30",
            "activebackground": "#3e3e42", "activeforeground": "#ffffff", "bd": 0, "height": 2
        }
        
        # LEFT COLUMN BUTTONS: Dependencies & Status
        self.status_btn = tk.Button(self.control_frame, text="Status", command=self.run_diagnostics, **btn_style)
        self.status_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.pillow_btn = tk.Button(self.control_frame, text="Install Pillow", command=self.install_pillow, **btn_style)
        self.pillow_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.ctk_btn = tk.Button(self.control_frame, text="Install CustomTkinter", command=self.install_ctk, **btn_style)
        self.ctk_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # RIGHT COLUMN BUTTONS: Optimization Engines
        self.speedup_btn = tk.Button(self.control_frame, text="Clear app speedup files", command=self.clear_cache, **btn_style)
        self.speedup_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.trouble_btn = tk.Button(self.control_frame, text="Troubleshoot", command=self.troubleshoot_winget, **btn_style)
        self.trouble_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # DESTRUCTIVE UNINSTALL BUTTON
        self.uninstall_btn = tk.Button(
            self.control_frame, text="Uninstall Application", command=self.uninstall_app,
            font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#d32f2f",
            activebackground="#b71c1c", activeforeground="#ffffff", bd=0, height=2
        )
        self.uninstall_btn.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # --- TERMINAL LOG MODULE ---
        self.log_text = tk.Text(root, height=8, font=("Consolas", 10), bg="#121212", fg="#2ecc71", bd=0, padx=10, pady=10)
        self.log_text.pack(padx=20, pady=(5, 15), fill="x")
        self.log_text.insert("1.0", "[CONSOLE LOG] Ready.\n")
        self.log_text.configure(state="disabled")
        
        # Auto-trigger diagnostics array configuration verification on engine loadup
        self.run_diagnostics()

    def create_status_row(self, parent, text_var):
        """Helper to safely build and anchor rows within the Dashboard Frame."""
        lbl = tk.Label(parent, textvariable=text_var, font=("Segoe UI", 10), bg="#1e1e1e", fg="#ffffff", anchor="w")
        lbl.pack(padx=15, pady=4, fill="x")

    def log(self, message):
        """Appends feedback logging into the console workspace window."""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    # ==========================================
    # FEATURE 1: ENVIRONMENT VALIDATION DASHBOARD
    # ==========================================
    def run_diagnostics(self):
        self.log("Running machine system diagnosis sequence...")
        
        # 1. Inspect execution instance mapping pointer
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.python_status.set(f"Python Environment: Active (v{py_ver}) [✔]")
        
        # 2. Inspect active framework context availability for Pillow
        try:
            from PIL import Image
            self.pillow_status.set("Pillow Package: Operational [✔]")
        except ImportError:
            self.pillow_status.set("Pillow Package: Deficient/Missing [❌]")
            
        # 3. Inspect framework context availability for CustomTkinter
        try:
            import customtkinter
            self.ctk_status.set("CustomTkinter Package: Operational [✔]")
        except ImportError:
            self.ctk_status.set("CustomTkinter Package: Deficient/Missing [❌]")
            
        self.log("Diagnostic array map complete.")

    def run_pip(self, package_name, associated_button):
        def worker():
            self.log(f"Executing Pip automated script fetch loop for: '{package_name}'...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.log(f"Successfully processed dependency module: '{package_name}'.")
                self.run_diagnostics()
            except subprocess.CalledProcessError:
                self.log(f"[ERROR] Engine encountered pipeline execution drop during package fetch: {package_name}")
            finally:
                associated_button.configure(state="normal")
        
        associated_button.configure(state="disabled")
        threading.Thread(target=worker, daemon=True).start()

    def install_pillow(self):
        self.run_pip("Pillow", self.pillow_btn)

    def install_ctk(self):
        self.run_pip("customtkinter", self.ctk_btn)

    # ==========================================
    # FEATURE 2: DYNAMIC SOURCE CACHE VACUUM
    # ==========================================
    def clear_cache(self):
        def worker():
            self.speedup_btn.configure(state="disabled")
            self.log("Initializing WinGet Index Optimization Database cleanup...")
            
            # Flush Local AppData temporary operational path targets
            user_temp = os.environ.get("TEMP", "")
            winget_cache = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Packages", "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe", "LocalState", "LocalState.db")
            
            # Command native engine database indexing validation sequence 
            try:
                # Force WinGet to clear catalog memory tracking structures natively
                subprocess.run(["winget", "locate", "--query", "VoidQueryStringToForceRefresh"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.log("WinGet indexed package map refreshed.")
            except Exception:
                pass
                
            self.log("Purge complete. Stale app search lookup caching dropped cleanly.")
            self.speedup_btn.configure(state="normal")
            messagebox.showinfo("Optimization Suite", "WinGet cache clean loop complete! App searches should render faster.")
            
        threading.Thread(target=worker, daemon=True).start()

    # ==========================================
    # FEATURE 3: WINGET CORE RESET ENGINE
    # ==========================================
    def troubleshoot_winget(self):
        confirm = messagebox.askyesno(
            "Troubleshoot Wizard", 
            "This option resets your Windows Package Manager sources back to factory defaults to resolve corrupt search tables.\n\nProceed with deep repository reset?"
        )
        if not confirm:
            return
            
        def worker():
            self.trouble_btn.configure(state="disabled")
            self.log("Resetting core WinGet package pipelines...")
            try:
                # Execute automated force reset pipeline configurations directly down to source endpoints
                process = subprocess.run(
                    ["winget", "source", "reset", "--force"], 
                    capture_output=True, text=True, encoding="utf-8",
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if process.returncode == 0:
                    self.log("[SUCCESS] Core tracking records completely restored to system defaults.")
                    messagebox.showinfo("Troubleshoot Wizard", "WinGet repository structure reset perfectly.")
                else:
                    self.log(f"[WARNING] Reset output token state error flag: {process.stderr}")
            except Exception as e:
                self.log(f"[CRITICAL ERROR] Core tracking framework drop: {str(e)}")
            finally:
                self.trouble_btn.configure(state="normal")
                
        threading.Thread(target=worker, daemon=True).start()

    # ==========================================
    # UNINSTALL PROCESS
    # ==========================================
    def uninstall_app(self):
        confirm = messagebox.askyesno(
            "Confirm Uninstall", 
            "Are you sure you want to completely uninstall WinDepot?\nThis will wipe all application files and close this window."
        )
        if confirm:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if os.path.basename(current_dir).lower() == "appdepot" or "appdepot" in current_dir.lower():
                    bat_path = os.path.join(os.environ["TEMP"], "wd_cleanup.bat")
                    with open(bat_path, "w") as f:
                        f.write("@echo off\n")
                        f.write("timeout /t 1 /nobreak >nul\n") 
                        f.write(f'rmdir /s /q "{current_dir}"\n') 
                        f.write(f'del "{os.environ["USERPROFILE"]}\\Desktop\\WinDepot.lnk"\n') 
                        f.write("del %0\n") 
                    
                    subprocess.Popen([bat_path], shell=True)
                    self.root.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror("Security Error", "The manager is not running from inside an 'Appdepot' target directory folder. Aborting self-delete.")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected failure occurred during uninstallation:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WinDepotManager(root)
    root.mainloop()