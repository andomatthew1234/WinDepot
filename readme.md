# ⬜ WinDepot

**The best app installer for Windows. Period.**  
Enter a search term. Click enter. Click install. Done.

<p align="center">
  <img src="https://raw.githubusercontent.com/andomatthew1234/WinDepot/main/assets/favicon.png" alt="WinDepot Logo" width="128">
</p>

## WinDepot app store features
* ⚡ **Built to be fast** WinDepot is built from the ground up to be the fastest app installer. It's fast to install, fast to search, and fast to download. With our new localSearch variable, the app install page loads almost instantly (less then 0.5s) and installed apps list even faster.
* 🏪 **Every. Single. App.** Everything on the Microsoft Store (excluding Xbox apps), plus the Winget store (basically every app on the planet) is on WinDepot.
* 💻 **Easy to use** WinDepot is easy to use - and looks good while it's at it. It syncs with your Windows theme and Windows Theme color for an unmatched UI. It also now comes with a Text size slider that lets you choose the size of the text in the list.
* 📋 **Installed apps lisr** WinDepot lets you see your installed apps and uninstall them in seconds - even restricted apps like Microsoft Edge!

## 🛠️ Tech Stack
* **Frontend / Backend:** Python, Pillow, TKinter, CustomTKinter
* **App installation:** Winget
* **WinDepot store installation:** Python + .bat scripts

## 🌐 How to use WinDepot after installation
1. Make sure WinDepot is installed! If it isn't, check the Installation page below. You can check if it's installed by seeing if there is a 'WinDepot' folder on your desktop.
2. Run WinDepot by double-clicking `store.py` in the AppDepot folder (on your desktop).

Note: there are other files in WinDepot. Here's what they do:
- `/assets` - our images for our homepage and branding
- `favicon.png` / `favicon.ico` - our logo images
- `installer.bat` - this is what you use to download WinDepot. It will download files. That's it.
- `manage_appdepot.py` - this is the python file you use for uninstalling and troubleshooting WinDepot.
- `python_installer.exe` - this app will install Python if you don't already have it on the setup.bat page
- `readme.md` - this is the text you're reading right now. Seriously.
- `setup.bat` - after running installer.bat, this downloads Pillow/CustomTKINTER (makes the app look good and functional), makes sure Python is installed (and installs it if it isn't), and adds the folder to your desktop.
- `store.py` - this is the actual app itself.
- Other `.zip` files - for our releases page

---

# ⚡ Lightning installation
*(Seriously, a 2yo could do this.)*

1. **Download** the installer by going to:  
   https://github.com/andomatthew1234/WinDepot/releases/latest/
2. **Double click** `installer.bat` that the website just downloaded.
3. **Select** Run to confirm the file will download.

*Windows may give you a scary "Publisher not verified" warning. That's expected because the installer isn't code-signed.*

### How the installer works

- Downloads the latest version of WinDepot (the whole ZIP file)
- Extracts the ZIP to a folder
- Opens that folder in the terminal and runs `setup.bat`

The `setup.bat` file will:

- Check Python is installed (and install it if it isn't)
- Install all required packages
- Deploy the application

---

# ... Other installation types

## Medium setup
*(Try this if Lightning doesn't work.)*

1. Download WinDepot by clicking the **Code** button at the top of the page > **Download ZIP**
2. Extract WinDepot by right-clicking the folder you downloaded > **Extract All**
3. Double-click on `setup.bat`. Our installer will:
   - Make sure Python is installed (and install it if it isn't)
   - Download all required files
   - Make sure you're ready to go
4. Run WinDepot by double-clicking `store.py`

---

## Manual setup
*(Not recommended.)*

It takes a few minutes, but here's how to install WinDepot.

### 1. Make sure Python is installed

The Python software must be installed to run WinDepot.

If you don't have it, get it from the Microsoft Store:

https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-GB&gl=AU

To confirm Python is installed:

Open Terminal or PowerShell and type:

```text
python --version
```

If it doesn't come back with a red error, you're ready to go.

### 2. Download the files

- Press the green **Code** button
- Select **Download ZIP**
- Open File Explorer
- Go to **Downloads**
- Right-click the ZIP file
- Select **Extract All**

### 3. Run the application

Double-click `store.py`.

If this does not work:

- Right-click `store.py`
- Select **Open with**
- Choose **Python**

### 4. Use the app!

You're ready to install all you want.

---

## 💡 Tip

You can pin WinDepot to the taskbar for easy access.

1. Right-click `store.py`
2. Select **Create shortcut**
3. Customize the icon and name if you want
4. Right-click the shortcut
5. Select **More options**
6. Select **Pin to taskbar**

---

<p align="center">
  <img src="https://raw.githubusercontent.com/andomatthew1234/WinDepot/main/assets/favicon.png" alt="WinDepot Logo" width="64">
</p>

<p align="center">
  <b>Created by Matthew Anderson</b>
</p>