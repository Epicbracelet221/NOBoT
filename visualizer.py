import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import collections

class SensorVisualizer:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        
        # Data storage
        self.max_points = 50
        self.data_history = collections.deque([0]*self.max_points, maxlen=self.max_points)
        
        # Setup Figure
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#101010')
        
        # 1. Line Graph (Distance over Time)
        self.ax_graph = self.fig.add_subplot(211)
        self.ax_graph.set_facecolor('#1a1a1a')
        self.line, = self.ax_graph.plot([], [], color='#00e676', linewidth=2)
        self.ax_graph.set_title("Ultrasonic Distance (cm)", color='white', fontsize=10)
        self.ax_graph.tick_params(axis='x', colors='white')
        self.ax_graph.tick_params(axis='y', colors='white')
        self.ax_graph.set_ylim(0, 400)
        self.ax_graph.grid(True, color='#333')

        # 2. Radar View (Polar Plot)
        self.ax_radar = self.fig.add_subplot(212, projection='polar')
        self.ax_radar.set_facecolor('#1a1a1a')
        self.ax_radar.set_title("Surroundings Radar", color='white', fontsize=10, pad=10)
        self.ax_radar.tick_params(axis='x', colors='white')
        self.ax_radar.tick_params(axis='y', colors='white')
        self.ax_radar.set_theta_zero_location('N')
        self.ax_radar.set_theta_direction(-1)
        self.ax_radar.set_rlim(0, 400)
        self.ax_radar.grid(True, color='#333')
        
        # Radar scatter point
        self.radar_point, = self.ax_radar.plot([], [], 'ro', markersize=8)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    def update(self, distance):
        # Update Data
        self.data_history.append(distance)
        
        # Update Line Graph
        self.line.set_data(range(len(self.data_history)), self.data_history)
        self.ax_graph.set_xlim(0, len(self.data_history))
        
        # Update Radar
        # Simulating a scan: We only have one sensor, so we just show a point at 0 degrees (Front)
        # To make it look like a "scan", we could fade old points, but for now, let's just show the current reading.
        if distance > 0:
            self.radar_point.set_data([0], [distance])
        else:
            self.radar_point.set_data([], [])

        self.canvas.draw()
