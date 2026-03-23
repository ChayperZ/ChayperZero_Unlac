import os
import binascii
import threading
import subprocess
import webbrowser
import sys
import ctypes
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image


try:
    myappid = 'chayperz.zero.pro.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

ctk.set_appearance_mode("Dark")


BG_COLOR = "#0F0F0F"
SIDEBAR_BG = "#161616"
BOX_BG = "#1E1E1E"
ACCENT_PURPLE = "#8E44AD"
GRAY_TABS = "#2C2C2C"

def resource_path(relative_path):
    """ الحصول على المسار الصحيح سواء كنت تشغل الكود أو EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ChayperZeroPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chayper Zero Pro")
        self.geometry("1300x850")
        self.configure(fg_color=BG_COLOR)


        self.setup_icon()


        self.jar_name = "unluac.jar"
        self.target_list = []
        self.output_folder = "Decompiled_Files"
        self.sidebar_visible = True
        self.file_checkboxes = {}


        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.setup_sidebar()
        self.setup_main_area()
        

        self.status_bar = ctk.CTkLabel(self, text="Status: Ready", anchor="w", padx=20, fg_color="#111", height=25)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def setup_icon(self):
        icon_path = resource_path("icon1.ico")
        if os.path.exists(icon_path):
            try:
                # الطريقة الأفضل لويندوز
                self.iconbitmap(icon_path)
                # إعادة التأكيد بعد قليل لضمان الظهور
                self.after(200, lambda: self.iconbitmap(icon_path))
            except:
                try:
                    # طريقة احتياطية باستخدام PIL
                    img = Image.open(icon_path)
                    self.iconphoto(False, ctk.CTkImage(light_image=img, dark_image=img)._light_image)
                except:
                    print("Could not load icon file.")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # اللوجو
        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                        dark_image=Image.open(logo_path),
                                        size=(140, 140))
                self.logo_lbl = ctk.CTkLabel(self.sidebar, image=logo_img, text="")
                self.logo_lbl.pack(pady=(30, 5))
            except:
                self.show_fallback_logo()
        else:
            self.show_fallback_logo()

        ctk.CTkLabel(self.sidebar, text="V 1.2 Edition", 
                     font=ctk.CTkFont(size=10, slant="italic"), 
                     text_color="#555").pack(pady=(0, 25))

        # أزرار الاستيراد
        input_box = ctk.CTkFrame(self.sidebar, fg_color=BOX_BG, corner_radius=15)
        input_box.pack(padx=15, pady=10, fill="x")
        
        ctk.CTkButton(input_box, text="📂 Import Files", fg_color="#252525", hover_color="#333", command=self.select_file).pack(padx=15, pady=8, fill="x")
        ctk.CTkButton(input_box, text="📁 Import Folder", fg_color="#252525", hover_color="#333", command=self.select_folder).pack(padx=15, pady=(0, 15), fill="x")

        # قائمة الملفات
        self.queue_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.queue_frame.pack(padx=15, pady=10, fill="both", expand=True)

        self.files_header = ctk.CTkButton(self.queue_frame, text="▼  LOADED QUEUE", font=ctk.CTkFont(size=12, weight="bold"),
                                          fg_color="#1A1A1A", anchor="w", command=self.toggle_files_list)
        self.files_header.pack(fill="x")

        self.files_container = ctk.CTkFrame(self.queue_frame, fg_color="#0C0C0C", corner_radius=10)
        self.files_container.pack(fill="both", expand=True, pady=5)

        self.file_scroll = ctk.CTkScrollableFrame(self.files_container, fg_color="transparent")
        self.file_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # رابط المطور
        link = ctk.CTkLabel(self.sidebar, text="Developed by ChayperZ", text_color="#444", font=ctk.CTkFont(size=10), cursor="hand2")
        link.pack(side="bottom", pady=15)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/ChayperZ"))

    def show_fallback_logo(self):
        ctk.CTkLabel(self.sidebar, text="CHAYPER ZERO", 
                     font=ctk.CTkFont(size=22, weight="bold"), 
                     text_color=ACCENT_PURPLE).pack(pady=(40, 5))

    def setup_main_area(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # التحكم العلوي
        self.top_nav = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_nav.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.toggle_btn = ctk.CTkButton(self.top_nav, text="☰", width=40, fg_color=GRAY_TABS, command=self.toggle_sidebar)
        self.toggle_btn.pack(side="left", padx=(0, 10))

        self.tab_switcher = ctk.CTkSegmentedButton(self.top_nav, values=["System Console", "Analysis Mode"],
                                                   command=self.switch_view, selected_color=ACCENT_PURPLE)
        self.tab_switcher.pack(side="left", fill="x", expand=True)
        self.tab_switcher.set("System Console")

        # واجهة الكونسول
        self.console_view = ctk.CTkFrame(self.main_container, fg_color=BOX_BG, corner_radius=15)
        self.console_view.grid_columnconfigure(0, weight=1)
        self.console_view.grid_rowconfigure(0, weight=1)
        self.console = ctk.CTkTextbox(self.console_view, font=("Consolas", 13), fg_color="#0A0A0A", text_color="#A569BD")
        self.console.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # واجهة التحليل (مخفية في البداية)
        self.analysis_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.analysis_view.grid_columnconfigure(0, weight=1)
        self.analysis_view.grid_columnconfigure(1, weight=3)
        self.analysis_view.grid_rowconfigure(0, weight=1)

        self.setup_analysis_ui()

        self.console_view.grid(row=1, column=0, sticky="nsew")

        # زر التشغيل السفلي
        self.start_btn = ctk.CTkButton(self.main_container, text="▶ START DECOMPILATION", font=ctk.CTkFont(size=16, weight="bold"),
                                       fg_color=ACCENT_PURPLE, height=50, width=300, corner_radius=25,
                                       command=self.run_thread, state="disabled")
        self.start_btn.grid(row=2, column=0, pady=20)

    def setup_analysis_ui(self):
        # قائمة الملفات في وضع التحليل
        self.file_list_analysis = ctk.CTkFrame(self.analysis_view, fg_color=BOX_BG, corner_radius=12)
        self.file_list_analysis.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.analysis_scroll = ctk.CTkScrollableFrame(self.file_list_analysis, fg_color="transparent")
        self.analysis_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # عرض الكود والـ Hex
        self.code_display = ctk.CTkFrame(self.analysis_view, fg_color=BOX_BG, corner_radius=12)
        self.code_display.grid(row=0, column=1, sticky="nsew")
        self.code_display.grid_columnconfigure((0, 1), weight=1)
        self.code_display.grid_rowconfigure(1, weight=1)

        self.hex_text = ctk.CTkTextbox(self.code_display, fg_color="#0A0A0A", font=("Consolas", 11))
        self.hex_text.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        self.lua_text = ctk.CTkTextbox(self.code_display, fg_color="#0A0A0A", font=("Consolas", 11))
        self.lua_text.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

    # --- الوظائف (Functions) ---

    def log(self, msg):
        self.console.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.console.see("end")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_forget()
        else:
            self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar_visible = not self.sidebar_visible

    def switch_view(self, value):
        if value == "System Console":
            self.analysis_view.grid_forget()
            self.console_view.grid(row=1, column=0, sticky="nsew")
        else:
            self.console_view.grid_forget()
            self.analysis_view.grid(row=1, column=0, sticky="nsew")

    def select_file(self):
        paths = filedialog.askopenfilenames(filetypes=[("Lua Files", "*.lua *.luac")])
        for p in paths:
            if p not in self.target_list: self.target_list.append(p)
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
        
        for path in self.target_list:
            name = os.path.basename(path)
            btn = ctk.CTkButton(self.file_scroll, text=name, fg_color="transparent", anchor="w", 
                               command=lambda p=path: self.load_file_data(p))
            btn.pack(fill="x", pady=1)
            
            ctk.CTkButton(self.analysis_scroll, text=f"📄 {name}", fg_color="transparent", anchor="w",
                          command=lambda p=path: self.load_file_data(p)).pack(fill="x", pady=1)

        self.start_btn.configure(state="normal" if self.target_list else "disabled")
        self.status_bar.configure(text=f"Status: {len(self.target_list)} files loaded")

    def load_file_data(self, path):
        try:
            with open(path, 'rb') as f:
                content = f.read(1000)
                hex_dump = binascii.hexlify(content, ' ', 16).decode('utf-8')
                self.hex_text.delete("0.0", "end")
                self.hex_text.insert("0.0", hex_dump)
            
            # عرض الكود المترجم إذا وجد
            base_name = os.path.splitext(os.path.basename(path))[0]
            out_name = os.path.join(self.output_folder, f"{base_name}.lua")
            self.lua_text.delete("0.0", "end")
            if os.path.exists(out_name):
                with open(out_name, "r", encoding="utf-8", errors="ignore") as f:
                    self.lua_text.insert("0.0", f.read())
            else:
                self.lua_text.insert("0.0", "-- [Wait] Run Decompilation first.")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_thread(self):
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        self.start_btn.configure(state="disabled", text="PROCESSING...")
        if not os.path.exists(self.output_folder): os.makedirs(self.output_folder)
        
        jar_path = resource_path(self.jar_name)
        if not os.path.exists(jar_path):
            self.log(f"ERROR: {self.jar_name} not found!")
            self.start_btn.configure(state="normal", text="▶ START")
            return

        success = 0
        for path in self.target_list:
            name = os.path.basename(path)
            self.log(f"Decompiling: {name}")
            # محاولة تشغيل جافا
            try:
                cmd = ["java", "-jar", jar_path, path]
                res = subprocess.run(cmd, capture_output=True, text=False)
                if res.returncode == 0:
                    out_p = os.path.join(self.output_folder, f"{os.path.splitext(name)[0]}.lua")
                    with open(out_p, "wb") as f: f.write(res.stdout)
                    success += 1
                    self.log(f"SUCCESS: {name}")
                else:
                    self.log(f"FAILED: {name}")
            except Exception as e:
                self.log(f"Runtime Error: {e}")

        self.start_btn.configure(state="normal", text="▶ START DECOMPILATION")
        messagebox.showinfo("Chayper Zero", f"Finished {success} files.")

    def toggle_files_list(self):
        if self.files_container.winfo_viewable():
            self.files_container.pack_forget()
        else:
            self.files_container.pack(fill="both", expand=True, pady=5)

if __name__ == "__main__":
    app = ChayperZeroPro()
    app.mainloop()