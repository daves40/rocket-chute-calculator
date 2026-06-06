from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class RecoveryPlotPanel:
    def __init__(self, parent):
        self.figure = Figure(figsize=(10, 8), dpi=100)

        self.altitude_axis = self.figure.add_subplot(311)
        self.distance_axis = self.figure.add_subplot(312)
        self.velocity_axis = self.figure.add_subplot(313)

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.draw_empty_plots()

    def draw_empty_plots(self):
        self.altitude_axis.clear()
        self.distance_axis.clear()
        self.velocity_axis.clear()

        self.altitude_axis.set_title("Altitude vs Time")
        self.altitude_axis.set_xlabel("Time (s)")
        self.altitude_axis.set_ylabel("Altitude AGL (ft)")
        self.altitude_axis.grid(True)

        self.distance_axis.set_title("Lateral Distance vs Time")
        self.distance_axis.set_xlabel("Time (s)")
        self.distance_axis.set_ylabel("Distance (ft)")
        self.distance_axis.grid(True)

        self.velocity_axis.set_title("Velocity vs Time")
        self.velocity_axis.set_xlabel("Time (s)")
        self.velocity_axis.set_ylabel("Velocity (ft/s)")
        self.velocity_axis.grid(True)

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def update(self, plot_data):
        time_s = plot_data["time_s"]
        altitude_ft = plot_data["altitude_ft"]
        lateral_distance_ft = plot_data["lateral_distance_ft"]
        vertical_velocity_fps = plot_data["vertical_velocity_fps"]
        horizontal_velocity_fps = plot_data["horizontal_velocity_fps"]
        total_velocity_fps = plot_data["total_velocity_fps"]

        self.altitude_axis.clear()
        self.distance_axis.clear()
        self.velocity_axis.clear()

        self.altitude_axis.plot(time_s, altitude_ft)
        self.altitude_axis.set_title("Altitude vs Time")
        self.altitude_axis.set_xlabel("Time (s)")
        self.altitude_axis.set_ylabel("Altitude AGL (ft)")
        self.altitude_axis.grid(True)

        self.distance_axis.plot(time_s, lateral_distance_ft)
        self.distance_axis.set_title("Lateral Distance vs Time")
        self.distance_axis.set_xlabel("Time (s)")
        self.distance_axis.set_ylabel("Distance (ft)")
        self.distance_axis.grid(True)

        self.velocity_axis.plot(time_s, total_velocity_fps, label="Total")
        self.velocity_axis.plot(time_s, vertical_velocity_fps, label="Vertical")
        self.velocity_axis.plot(time_s, horizontal_velocity_fps, label="Horizontal")
        self.velocity_axis.set_title("Velocity vs Time")
        self.velocity_axis.set_xlabel("Time (s)")
        self.velocity_axis.set_ylabel("Velocity (ft/s)")
        self.velocity_axis.legend()
        self.velocity_axis.grid(True)

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()