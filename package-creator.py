import os
import zipfile
import tkinter as tk
from tkinter import messagebox
import threading

# =========================
# ZIP CREATION
# =========================
def create_zip(version):
    base_dir = os.getcwd()
    # Name the zip file based on the version provided
    zip_name = f"windepot_{version}.zip"  
    zip_path = os.path.join(base_dir, zip_name)

    # Folders we DO NOT want in the final zip
    exclude_dirs = {".git", "__pycache__", ".vscode", ".idea"}
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                # Exclude old zips and the builder script itself
                if file.endswith(".zip") or file == os.path.basename(__file__):
                    continue

                file_path = os.path.join(root, file)

                # Avoid recursion loop (don't zip the zip we are currently making)
                if file_path == zip_path:
                    continue

                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)

    return zip_path

# =========================
# UI THREADING & ACTION
# =========================
def on_submit():
    version = entry.get().strip()

    if not version:
        messagebox.showwarning("Input Missing", "Please enter a version number.")
        return

    btn.config(text="Compressing...", state="disabled")
    
    # Run the heavy lifting in a background thread so the UI doesn't freeze
    def worker():
        try:
            zip_path = create_zip(version)
            # Notify success on the main thread
            root.after(0, lambda: messagebox.showinfo("Success", f"Successfully created:\n{os.path.basename(zip_path)}"))
        except Exception as e:
            root.after(0, lambda err=e: messagebox.showerror("Zip Error", str(err)))
        finally:
            # Reset the button
            root.after(0, lambda: btn.config(text="Create ZIP File", state="normal"))

    threading.Thread(target=worker, daemon=True).start()

# =========================
# UI SETUP
# =========================
root = tk.Tk()
root.title("WinDepot Packager")
root.geometry("340x150")
root.resizable(False, False)

label = tk.Label(root, text="Enter version (e.g. 1.2.1)")
label.pack(pady=10)

entry = tk.Entry(root, width=25)
entry.pack()

btn = tk.Button(root, text="Create ZIP File", command=on_submit)
btn.pack(pady=15)

root.mainloop()