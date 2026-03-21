import os
import binascii
import threading
import subprocess
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image # تأكد من تثبيت Pillow

# ================== Appearance ==================
ctk.set_appearance_mode("Dark")

# ================== Color Palette ==================
BG_COLOR = "#0F0F0F"
SIDEBAR_BG = "#161616"
BOX_BG = "#1E1E1E"
ACCENT_PURPLE = "#8E44AD"
GRAY_TABS = "#2C2C2C"
import sys

def resource_path(relative_path):
  
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ChayperZeroPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Chayper Zero")
        self.geometry("1300x850")
        self.configure(fg_color=BG_COLOR)

        # --- State Variables ---
        self.jar_name = "unluac.jar"
        self.target_list = []
        self.output_folder = "Decompiled_Files"
        self.sidebar_visible = True
        self.file_checkboxes = {}

        # --- Layout Grid ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Setup Sidebar
        self.setup_sidebar()

        # 2. Setup Main Content
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1) 
        self.main_container.grid_rowconfigure(2, weight=0) 

        # --- Top Navigation ---
        self.top_nav = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_nav.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.toggle_btn = ctk.CTkButton(self.top_nav, text="☰", width=40, fg_color=GRAY_TABS, hover_color="#3D3D3D", command=self.toggle_sidebar)
        self.toggle_btn.pack(side="left", padx=(0, 10))

        self.tab_switcher = ctk.CTkSegmentedButton(
            self.top_nav, 
            values=["System Console", "Analysis Mode"],
            command=self.switch_view,
            selected_color=ACCENT_PURPLE,
            unselected_color="#1A1A1A",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.tab_switcher.pack(side="left", fill="x", expand=True)
        self.tab_switcher.set("System Console")

        # --- Views Setup ---
        self.console_view = ctk.CTkFrame(self.main_container, fg_color=BOX_BG, corner_radius=15)
        self.console_view.grid_columnconfigure(0, weight=1)
        self.console_view.grid_rowconfigure(0, weight=1)
        self.console = ctk.CTkTextbox(self.console_view, font=("Consolas", 13), fg_color="#0A0A0A", text_color="#A569BD")
        self.console.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.analysis_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.analysis_view.grid_columnconfigure(0, weight=1)
        self.analysis_view.grid_columnconfigure(1, weight=3)
        self.analysis_view.grid_rowconfigure(0, weight=1)

        self.file_list_analysis = ctk.CTkFrame(self.analysis_view, fg_color=BOX_BG, corner_radius=12)
        self.file_list_analysis.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.file_list_analysis, text="ANALYSIS LIST", font=("Segoe UI", 12, "bold"), text_color="gray").pack(pady=10)
        
        self.analysis_scroll = ctk.CTkScrollableFrame(self.file_list_analysis, fg_color="transparent")
        self.analysis_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.code_display = ctk.CTkFrame(self.analysis_view, fg_color=BOX_BG, corner_radius=12)
        self.code_display.grid(row=0, column=1, sticky="nsew")
        self.code_display.grid_columnconfigure((0, 1), weight=1)
        self.code_display.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.code_display, text="Bytecode (Hex)", text_color=ACCENT_PURPLE, font=("Consolas", 12, "bold")).grid(row=0, column=0, pady=10)
        ctk.CTkLabel(self.code_display, text="Lua Source", text_color=ACCENT_PURPLE, font=("Consolas", 12, "bold")).grid(row=0, column=1, pady=10)

        self.hex_text = ctk.CTkTextbox(self.code_display, fg_color="#0A0A0A", font=("Consolas", 11), wrap="none")
        self.hex_text.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        self.lua_text = ctk.CTkTextbox(self.code_display, fg_color="#0A0A0A", font=("Consolas", 11), wrap="none")
        self.lua_text.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.console_view.grid(row=1, column=0, sticky="nsew") 

        self.action_bar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_bar.grid(row=2, column=0, sticky="ew", pady=20)
        
        self.start_btn = ctk.CTkButton(
            self.action_bar, 
            text="▶ START DECOMPILATION", 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=ACCENT_PURPLE,
            hover_color="#732D91",
            height=50,
            width=300,
            corner_radius=25,
            command=self.run_thread,
            state="disabled"
        )
        self.start_btn.pack(expand=True)

        self.status_bar = ctk.CTkLabel(self, text="Status: Ready", anchor="w", padx=20, fg_color="#111", height=25)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    # ================== Sidebar UI ==================
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # --- Logo Logic ---
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"),
                                    dark_image=Image.open("logo.png"),
                                    size=(140, 140))
            self.logo_lbl = ctk.CTkLabel(self.sidebar, image=logo_img, text="")
            self.logo_lbl.pack(pady=(30, 5))
        except:
            ctk.CTkLabel(self.sidebar, text="CHAYPER ZERO", 
                         font=ctk.CTkFont(size=22, weight="bold"), 
                         text_color=ACCENT_PURPLE).pack(pady=(40, 5))

        ctk.CTkLabel(self.sidebar, text="V 1.0 Edition", 
                     font=ctk.CTkFont(size=10, slant="italic"), 
                     text_color="#555").pack(pady=(0, 25))

        # Core Actions
        input_box = ctk.CTkFrame(self.sidebar, fg_color=BOX_BG, corner_radius=15, border_width=1, border_color="#252525")
        input_box.pack(padx=15, pady=10, fill="x")
        
        ctk.CTkButton(input_box, text="📂 Import Files", fg_color="#252525", hover_color="#333", height=35, command=self.select_file).pack(padx=15, pady=8, fill="x")
        ctk.CTkButton(input_box, text="📁 Import Folder", fg_color="#252525", hover_color="#333", height=35, command=self.select_folder).pack(padx=15, pady=(0, 15), fill="x")

        # Modern Collapsible Queue
        self.queue_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.queue_frame.pack(padx=15, pady=10, fill="both", expand=True)

        self.files_header = ctk.CTkButton(
            self.queue_frame, text="▼  LOADED QUEUE", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1A1A1A", hover_color="#222", anchor="w",
            height=40, corner_radius=10, command=self.toggle_files_list
        )
        self.files_header.pack(fill="x")

        self.files_container = ctk.CTkFrame(self.queue_frame, fg_color="#0C0C0C", corner_radius=10)
        self.files_container.pack(fill="both", expand=True, pady=5)

        ctrl_bar = ctk.CTkFrame(self.files_container, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkButton(ctrl_bar, text="All", width=40, height=20, font=("Arial", 10), command=self.select_all_files).pack(side="left", padx=2)
        ctk.CTkButton(ctrl_bar, text="Clear", width=40, height=20, font=("Arial", 10), command=self.deselect_all_files).pack(side="left", padx=2)
        ctk.CTkButton(ctrl_bar, text="🗑 Remove", width=70, height=20, fg_color="#4E1A1A", hover_color="#7B241C", command=self.remove_selected_files).pack(side="right", padx=2)

        self.file_scroll = ctk.CTkScrollableFrame(self.files_container, fg_color="transparent", height=300)
        self.file_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        link = ctk.CTkLabel(self.sidebar, text="Developed by ChayperZ", text_color="#444", font=ctk.CTkFont(size=10), cursor="hand2")
        link.pack(side="bottom", pady=15)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/ChayperZ"))

    # ================== Logic Functions ==================
    def toggle_files_list(self):
        if self.files_container.winfo_viewable():
            self.files_container.pack_forget()
            self.files_header.configure(text="▶  LOADED QUEUE")
        else:
            self.files_container.pack(fill="both", expand=True, pady=5)
            self.files_header.configure(text="▼  LOADED QUEUE")

    def select_all_files(self):
        for var in self.file_checkboxes.values(): var.set(True)

    def deselect_all_files(self):
        for var in self.file_checkboxes.values(): var.set(False)

    def remove_selected_files(self):
        to_remove = [p for p, v in self.file_checkboxes.items() if v.get()]
        self.target_list = [p for p in self.target_list if p not in to_remove]
        self.update_ready_state()

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Lua Files", "*.lua *.luac")])
        if path and path not in self.target_list:
            self.target_list.append(path)
            self.update_ready_state()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.endswith(('.lua', '.luac')):
                        p = os.path.join(root, f)
                        if p not in self.target_list: self.target_list.append(p)
            self.update_ready_state()

    def update_ready_state(self):
        for w in self.file_scroll.winfo_children(): w.destroy()
        for w in self.analysis_scroll.winfo_children(): w.destroy()
        self.file_checkboxes.clear()

        for path in self.target_list:
            name = os.path.basename(path)
            var = ctk.BooleanVar(value=False)
            self.file_checkboxes[path] = var

            card = ctk.CTkFrame(self.file_scroll, fg_color="#161616", corner_radius=8, height=35)
            card.pack(fill="x", pady=2, padx=2)
            card.pack_propagate(False)

            cb = ctk.CTkCheckBox(card, text="", variable=var, width=20, checkbox_width=16, checkbox_height=16)
            cb.pack(side="left", padx=(10, 5))

            btn = ctk.CTkButton(card, text=name, font=ctk.CTkFont(size=12), fg_color="transparent", text_color="#BBB", anchor="w",
                               command=lambda p=path: self.load_file_data(p))
            btn.pack(side="left", fill="both", expand=True)
            
            ctk.CTkButton(self.analysis_scroll, text=f"📄 {name}", fg_color="transparent", anchor="w", height=30,
                          command=lambda p=path: self.load_file_data(p)).pack(fill="x", pady=1)

        count = len(self.target_list)
        self.start_btn.configure(state="normal" if count > 0 else "disabled")
        self.status_bar.configure(text=f"Status: {count} files loaded")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self.sidebar_visible = True

    def switch_view(self, value):
        if value == "System Console":
            self.analysis_view.grid_forget()
            self.console_view.grid(row=1, column=0, sticky="nsew")
        else:
            self.console_view.grid_forget()
            self.analysis_view.grid(row=1, column=0, sticky="nsew")

    def load_file_data(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    content = f.read(2000)
                    hex_dump = binascii.hexlify(content, ' ', 16).decode('utf-8')
                    formatted_hex = '\n'.join(hex_dump[i:i+48] for i in range(0, len(hex_dump), 48))
                self.hex_text.delete("0.0", "end")
                self.hex_text.insert("0.0", formatted_hex)

            base_name = os.path.splitext(os.path.basename(path))[0]
            out_name = os.path.join(self.output_folder, f"{base_name}.lua")
            self.lua_text.delete("0.0", "end")
            if os.path.exists(out_name):
                with open(out_name, "r", encoding="utf-8", errors="ignore") as f:
                    self.lua_text.insert("0.0", f.read())
            else:
                self.lua_text.insert("0.0", "-- [Wait] File not decompiled yet.")
        except Exception as e:
            self.log(f"Error viewing file: {e}")

    def log(self, msg):
        self.console.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.console.see("end")

    def run_thread(self):
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        self.start_btn.configure(state="disabled", text="PROCESSING...")
        if not os.path.exists(self.output_folder): os.makedirs(self.output_folder)
        
        if not os.path.exists(self.jar_name):
            self.log("ERROR: unluac.jar not found!")
            self.start_btn.configure(state="normal", text="▶ START")
            return

        success = 0
        for path in self.target_list:
            name = os.path.basename(path)
            self.log(f"Decompiling: {name}")
            cmd = ["java", "-jar", self.jar_name, path]
            res = subprocess.run(cmd, capture_output=True, text=False)
            if res.returncode == 0:
                out_p = os.path.join(self.output_folder, f"{os.path.splitext(name)[0]}.lua")
                with open(out_p, "wb") as f: f.write(res.stdout)
                success += 1
                self.log(f"SUCCESS: {name}")
            else: self.log(f"FAILED: {name}")

        self.start_btn.configure(state="normal", text="▶ START DECOMPILATION")
        messagebox.showinfo("Chayper Zero", f"Finished {success} files.")

if __name__ == "__main__":
    app = ChayperZeroPro()
    app.mainloop()