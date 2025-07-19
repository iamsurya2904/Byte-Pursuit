<h1 align="center">🛡️ Byte Pursuit Signature-Based Recovery Tool</h1>
<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/tech-stack-Python%20%7C%20GTK%20%7C%20AES-blue" alt="Tech Stack">
  <img src="https://img.shields.io/github/license/iamsurya2904/Shadow-Fox" alt="License">
</p>

---

## 🏆 Achievements

> 🚀 **Presented at Smart India Hackathon 2024 – Grand Finale**  
> 📍 Hosted at **IIT Jammu**  
> 🧬 **Officially recognized by the Forensics Department** for its relevance in digital evidence recovery and forensic workflows.

This project stood out for its lightweight architecture, on-device disk analysis capability, and secure-by-design recovery logic—particularly suitable for law enforcement and forensic labs operating in constrained environments.

---

## 🌐 Overview

** Signature-Based Recovery Tool** is a GUI-based Python application designed for forensic-grade file recovery. Built using **PyGObject (GTK+ 3)**, the tool provides an intuitive modern UI to recover encrypted logs, JPG/PNG images, and PDFs from raw disk paths using signature carving and AES decryption logic.

Designed with modern UI principles, sudo permission checks, and dynamic disk scanning—this tool is ideal for cybersecurity students, forensic analysts, and recovery engineers.

---

## 🧰 Key Features

✅ Stylish GTK3 GUI with dark theme + CSS styling  
✅ Sudo validation & `lsblk` disk enumeration  
✅ Recover:
- 📄 **PDFs** (`%PDF` → `%%EOF`)
- 🖼️ **JPGs** (`FFD8FFE0` → `FFD9`)
- 🖼️ **PNGs** (`89504E47...` → `IEND`)  
✅ Custom **log extraction & AES decryption** for embedded log signatures  
✅ Live progress tracking via a progress bar  
✅ Integrated log window for recovery feedback  
✅ Manual or `lsblk`-based drive selection

---

## 🖥️ UI Preview

> *(Insert screenshots here when ready)*

- Dark-themed window with rounded buttons
- Dropdown to choose file type
- Buttons for input/output, recovery, and reset
- Scrollable logging area for operation tracking

---

## 🧱 Technologies Used

- **Python 3.10+**
- `gi.repository` (PyGObject for GTK GUI)
- `cryptography` library (AES decryption)
- `subprocess`, `re`, `threading`, `platform`
- Linux utilities: `lsblk`, `sudo`

---

## 🚀 Getting Started

### 🔧 Prerequisites

- Linux OS with GTK+ 3
- Python packages:
  ```bash
  sudo apt install python3-gi gir1.2-gtk-3.0
  pip install cryptography
🛠 Installation
bash
Copy
Edit
git clone https://github.com/iamsurya2904/Shadow-Fox.git
cd Shadow-Fox
python3 singnature\ based.py
⚠️ Run with sudo if required:

bash
Copy
Edit
sudo python3 singnature\ based.py
📦 File Structure
bash
Copy
Edit
Shadow-Fox/
│
├── templates/                # HTML UI assets (optional)
├── uploads/                  # Output folder for recovered files
├── singnature based.py       # Main recovery application
├── ...
🧪 How It Works
User selects a drive using lsblk or manually.

Chooses file type from dropdown (JPG, PNG, PDF, LOG).

The system reads raw disk data.

Signature-based pattern matching extracts file segments.

Decryption (for logs) is handled via AES (CFB mode).

Recovered files are saved in the output folder.

GUI logs all operations and shows progress.

⚙️ Customization
Edit AES Key & IV in singnature based.py:

python
Copy
Edit
decryption_key = b"1234567890abcdef"
iv = b"abcdef1234567890"
Replace these with your secure key/IV as per the use case.

🙋‍♂️ Author
Surya R
Cybersecurity Engineer & Python Developer
🔗 GitHub | LinkedIn

📜 License
This project is licensed under the MIT License – see the LICENSE file for details.

💭 Final Words
"In a digital world of noise and chaos, let your code recover the whispers of the past."

✨ Future Enhancements
🔐 Encrypted key vault for AES keys

📊 Disk usage analytics

🔍 Preview pane for recovered files

📤 Upload to secure S3/FTP storage
