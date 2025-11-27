import tkinter as tk
from tkinter import Label, Button, Frame, Scale, HORIZONTAL, StringVar, OptionMenu
from PIL import Image, ImageTk
import threading
import time
import queue

# Import Modules
from modules.comms import CommunicationManager
from modules.vision import VisionSystem
from modules.visualizer import SensorVisualizer
from modules.utils import KNOWN_WIDTHS, DEFAULT_FOCAL_LENGTH

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Bot | Advanced Vision & Control")
        self.root.geometry("1400x900")
        self.root.configure(bg="#101010")

        # --- Modules ---
        self.comms = CommunicationManager()
        self.vision = VisionSystem()
        
        # --- State ---
        self.camera_mode = "BOTH" # RGB, THERMAL, BOTH
        self.running = False

        # --- UI Setup ---
        self.setup_ui()
        
        # --- Start Update Loop ---
        self.update_gui()

    def setup_ui(self):
        # 1. Sidebar (Left)
        sidebar = Frame(self.root, bg="#1a1a1a", width=320)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Header
        Label(sidebar, text="SPIDER BOT", font=("Segoe UI", 24, "bold"), fg="#00e676", bg="#1a1a1a").pack(pady=(40, 5))
        Label(sidebar, text="Command Center", font=("Segoe UI", 12), fg="#888", bg="#1a1a1a").pack()

        # Divider
        Frame(sidebar, bg="#333", height=1).pack(fill=tk.X, padx=20, pady=20)

        # System Controls
        ctrl_frame = Frame(sidebar, bg="#1a1a1a")
        ctrl_frame.pack(fill=tk.X, padx=20)
        
        self.btn_start = self.create_button(ctrl_frame, "▶ START SYSTEM", "#2e7d32", self.start_system)
        self.btn_start.pack(fill=tk.X, pady=5)
        
        self.btn_stop = self.create_button(ctrl_frame, "⏹ STOP SYSTEM", "#c62828", self.stop_system)
        self.btn_stop.pack(fill=tk.X, pady=5)

        # Camera Toggles
        Label(sidebar, text="CAMERA FEED", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(30, 10))
        
        cam_frame = Frame(sidebar, bg="#1a1a1a")
        cam_frame.pack(fill=tk.X, padx=20)
        
        self.create_button(cam_frame, "RGB Only", "#333", lambda: self.set_cam_mode("RGB")).pack(fill=tk.X, pady=2)
        self.create_button(cam_frame, "Thermal Only", "#333", lambda: self.set_cam_mode("THERMAL")).pack(fill=tk.X, pady=2)
        self.create_button(cam_frame, "Dual View", "#333", lambda: self.set_cam_mode("BOTH")).pack(fill=tk.X, pady=2)

        # Bluetooth
        Label(sidebar, text="CONNECTION", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(30, 10))
        
        bt_frame = Frame(sidebar, bg="#1a1a1a")
        bt_frame.pack(fill=tk.X, padx=20)
        
        self.port_var = StringVar()
        self.port_menu = OptionMenu(bt_frame, self.port_var, "")
        self.port_menu.config(bg="#333", fg="white", bd=0, highlightthickness=0)
        self.port_menu.pack(fill=tk.X, pady=5)
        
        self.create_button(bt_frame, "↻ Refresh Ports", "#444", self.refresh_ports).pack(fill=tk.X, pady=2)
        self.btn_connect = self.create_button(bt_frame, "Connect", "#0277bd", self.toggle_connection)
        self.btn_connect.pack(fill=tk.X, pady=5)
        
        self.lbl_status = Label(bt_frame, text="Disconnected", font=("Segoe UI", 9), fg="#777", bg="#1a1a1a")
        self.lbl_status.pack(fill=tk.X)

        # Exit Button
        exit_frame = Frame(sidebar, bg="#1a1a1a")
        exit_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        self.create_button(exit_frame, "EXIT APPLICATION", "#b71c1c", self.on_closing).pack(fill=tk.X)

        # Robot Control
        Label(sidebar, text="MANUAL CONTROL", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(30, 10))
        
        grid_frame = Frame(sidebar, bg="#1a1a1a")
        grid_frame.pack(padx=20)
        
        self.create_button(grid_frame, "▲", "#333", lambda: self.comms.send_command('F')).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "◀", "#333", lambda: self.comms.send_command('L')).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "⏹", "#d32f2f", lambda: self.comms.send_command('S')).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "▶", "#333", lambda: self.comms.send_command('R')).grid(row=1, column=2, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "▼", "#333", lambda: self.comms.send_command('B')).grid(row=2, column=1, padx=2, pady=2, sticky="ew")

        # 2. Main Content (Right)
        main_content = Frame(self.root, bg="#101010")
        main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Top: Camera Feeds
        self.cam_container = Frame(main_content, bg="#000")
        self.cam_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.rgb_label = Label(self.cam_container, text="RGB FEED OFF", bg="black", fg="#333", font=("Segoe UI", 20))
        self.thermal_label = Label(self.cam_container, text="THERMAL FEED OFF", bg="black", fg="#333", font=("Segoe UI", 20))

        # Bottom: Visualizer
        vis_frame = Frame(main_content, bg="#1a1a1a", height=300)
        vis_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        vis_frame.pack_propagate(False)
        
        self.visualizer = SensorVisualizer(vis_frame)

        # Initial Layout
        self.set_cam_mode("BOTH")
        self.refresh_ports()

    def create_button(self, parent, text, color, cmd):
        return Button(parent, text=text, font=("Segoe UI", 10, "bold"), 
                      bg=color, fg="white", bd=0, activebackground=color,
                      command=cmd, cursor="hand2")

    def set_cam_mode(self, mode):
        self.camera_mode = mode
        # Clear current pack
        self.rgb_label.pack_forget()
        self.thermal_label.pack_forget()
        
        if mode == "RGB":
            self.rgb_label.pack(fill=tk.BOTH, expand=True)
        elif mode == "THERMAL":
            self.thermal_label.pack(fill=tk.BOTH, expand=True)
        else: # BOTH
            self.rgb_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            self.thermal_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

    def refresh_ports(self):
        ports = self.comms.get_available_ports()
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for p in ports:
            menu.add_command(label=p, command=lambda value=p: self.port_var.set(value))
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("No Ports")

    def toggle_connection(self):
        if not self.comms.is_connected:
            port = self.port_var.get()
            if not port or port == "No Ports": return
            
            success, msg = self.comms.connect(port)
            if success:
                self.btn_connect.config(text="Disconnect", bg="#c62828")
                self.lbl_status.config(text=msg, fg="#4caf50")
            else:
                self.lbl_status.config(text=msg, fg="red")
        else:
            self.comms.disconnect()
            self.btn_connect.config(text="Connect", bg="#0277bd")
            self.lbl_status.config(text="Disconnected", fg="#777")

    def start_system(self):
        if not self.running:
            self.running = True
            self.vision.start()

    def stop_system(self):
        self.running = False
        self.vision.stop()
        self.rgb_label.config(image='')
        self.thermal_label.config(image='')

    def update_gui(self):
        if self.running:
            # Update RGB
            try:
                img = self.vision.frame_queue.get_nowait()
                imgtk = ImageTk.PhotoImage(image=img)
                self.rgb_label.imgtk = imgtk
                self.rgb_label.configure(image=imgtk)
            except queue.Empty:
                pass

            # Update Thermal
            try:
                img_t = self.vision.thermal_queue.get_nowait()
                imgtk_t = ImageTk.PhotoImage(image=img_t)
                self.thermal_label.imgtk = imgtk_t
                self.thermal_label.configure(image=imgtk_t)
            except queue.Empty:
                pass

            # Update Sensors
            dist = self.comms.get_distance()
            self.visualizer.update(dist)

        self.root.after(30, self.update_gui)

    def on_closing(self):
        self.stop_system()
        self.comms.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
