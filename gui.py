import tkinter as tk
from tkinter import ttk, messagebox
import threading

from parachutes import Parachutes
from simulator import ParachuteDescentSimulator
from rocket import Rocket
from plotting import RecoveryPlotPanel


class RecoverySimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rocket Recovery Simulator")
        self.root.geometry("1200x900")

        self.parachute_rows = []

        self.create_tabs()
        self.create_rocket_inputs()
        self.create_parachute_section()
        self.create_run_button()
        self.create_output_box()
        self.create_plot_area()

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.input_tab = ttk.Frame(self.notebook)
        self.plot_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.input_tab, text="Inputs / Results")
        self.notebook.add(self.plot_tab, text="Plots")

    def create_rocket_inputs(self):
        rocket_frame = ttk.LabelFrame(self.input_tab, text="Rocket Parameters")
        rocket_frame.pack(fill="x", padx=10, pady=10)

        self.rocket_name = self.add_labeled_entry(rocket_frame, "Rocket Name", "STAR Rocket", 0)
        self.mass_kg = self.add_labeled_entry(rocket_frame, "Mass (kg)", "90", 1)
        self.apogee_ft = self.add_labeled_entry(rocket_frame, "Apogee (ft)", "10000", 2)
        self.launch_elevation_ft = self.add_labeled_entry(rocket_frame, "Launch Site Elevation (ft)", "2000", 3)
        self.initial_horizontal_velocity_fps = self.add_labeled_entry(
            rocket_frame, "Initial Horizontal Velocity (ft/s)", "100", 4
        )
        self.wind_speed_mph = self.add_labeled_entry(rocket_frame, "Wind Speed (mph)", "15", 5)

    def add_labeled_entry(self, parent, label_text, default_value, row):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="w", padx=5, pady=3)

        entry = ttk.Entry(parent)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=3)

        return entry
    
    def create_parachute_headers(self):
        headers = [
            "Name",
            "Diameter (in)",
            "Cd",
            "Deploy Alt. (ft)",
            "Deploy Time (s)",
            "At Apogee",
            "Reefing",
            ""
        ]

        for col, text in enumerate(headers):
            label = ttk.Label(
                self.parachute_table,
                text=text,
                anchor="center"
            )
            label.grid(row=0, column=col, padx=4, pady=4, sticky="ew")

        # Column sizing
        self.parachute_table.columnconfigure(0, weight=2, minsize=130)  # Name
        self.parachute_table.columnconfigure(1, weight=1, minsize=100)  # Diameter
        self.parachute_table.columnconfigure(2, weight=1, minsize=60)   # Cd
        self.parachute_table.columnconfigure(3, weight=1, minsize=120)  # Deploy altitude
        self.parachute_table.columnconfigure(4, weight=1, minsize=120)  # Deploy time
        self.parachute_table.columnconfigure(5, weight=1, minsize=90)   # At apogee
        self.parachute_table.columnconfigure(6, weight=1, minsize=80)   # Reefing
        self.parachute_table.columnconfigure(7, weight=1, minsize=80)   # Remove button

    def create_parachute_section(self):
        self.chute_frame = ttk.LabelFrame(self.input_tab, text="Parachutes")
        self.chute_frame.pack(fill="x", padx=10, pady=10)

        add_button = ttk.Button(
            self.chute_frame,
            text="Add Parachute",
            command=self.add_parachute_row
        )
        add_button.pack(anchor="w", padx=5, pady=5)

        # This frame holds the aligned table
        self.parachute_table = ttk.Frame(self.chute_frame)
        self.parachute_table.pack(fill="x", padx=5, pady=5)

        self.create_parachute_headers()

        self.add_parachute_row("Small Drogue", 48, 2.2, 10000, 1.8, True, 0.5)
        self.add_parachute_row("Big Drogue", 60, 2.2, 5000, 1.8, False, 0.5)
        self.add_parachute_row("Small Main", 96, 2.2, 3000, 2.3, False, 0.5)
        self.add_parachute_row("Main", 120, 2.2, 1200, 2.3, False, 1.0)

    def refresh_parachute_rows(self):
        for display_index, row in enumerate(self.parachute_rows, start=1):
            row["row_index"] = display_index

            for col, widget in enumerate(row["widgets"]):
                widget.grid(
                    row=display_index,
                    column=col,
                    padx=4,
                    pady=3,
                    sticky="ew" if col != 5 else ""
                )

    def add_parachute_row(
        self,
        name="",
        diameter=0,
        cd=2.2,
        deploy_altitude=0,
        deploy_time=1.0,
        deploy_at_apogee=False,
        reefing_factor=1.0
    ):
        row_index = len(self.parachute_rows) + 1

        name_entry = ttk.Entry(self.parachute_table)
        diameter_entry = ttk.Entry(self.parachute_table)
        cd_entry = ttk.Entry(self.parachute_table)
        altitude_entry = ttk.Entry(self.parachute_table)
        time_entry = ttk.Entry(self.parachute_table)
        apogee_var = tk.BooleanVar(value=deploy_at_apogee)
        apogee_check = ttk.Checkbutton(self.parachute_table, variable=apogee_var)
        reefing_entry = ttk.Entry(self.parachute_table)
        remove_button = ttk.Button(self.parachute_table, text="Remove")

        name_entry.insert(0, str(name))
        diameter_entry.insert(0, str(diameter))
        cd_entry.insert(0, str(cd))
        altitude_entry.insert(0, str(deploy_altitude))
        time_entry.insert(0, str(deploy_time))
        reefing_entry.insert(0, str(reefing_factor))

        row_data = {
            "row_index": row_index,
            "name": name_entry,
            "diameter": diameter_entry,
            "cd": cd_entry,
            "deploy_altitude": altitude_entry,
            "deploy_time": time_entry,
            "deploy_at_apogee": apogee_var,
            "reefing_factor": reefing_entry,
            "widgets": [
                name_entry,
                diameter_entry,
                cd_entry,
                altitude_entry,
                time_entry,
                apogee_check,
                reefing_entry,
                remove_button
            ]
        }

        remove_button.config(command=lambda row=row_data: self.remove_parachute_row(row))

        self.parachute_rows.append(row_data)

        self.refresh_parachute_rows()

    def remove_parachute_row(self, row_data):
        for widget in row_data["widgets"]:
            widget.destroy()

        self.parachute_rows.remove(row_data)
        self.refresh_parachute_rows()

    def create_run_button(self):
        self.run_button = ttk.Button(
            self.input_tab,
            text="Run Simulation",
            command=self.run_simulation
        )
        self.run_button.pack(pady=10)

    def create_output_box(self):
        output_frame = ttk.LabelFrame(self.input_tab, text="Simulation Output")
        output_frame.pack(fill="x", expand=False, padx=10, pady=10)

        self.output_text = tk.Text(output_frame, height=8)
        self.output_text.pack(fill="x", expand=False)

    def run_simulation(self):
        self.run_button.config(state="disabled")

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Running simulation...\n")

        thread = threading.Thread(target=self.run_simulation_worker)
        thread.daemon = True
        thread.start()

    def run_simulation_worker(self):
        try:
            rocket = Rocket(
                name=self.rocket_name.get(),
                total_mass_kg=float(self.mass_kg.get()),
                apogee_ft=float(self.apogee_ft.get()),
                launch_site_elevation_ft=float(self.launch_elevation_ft.get()),
                initial_horizontal_velocity_fps=float(self.initial_horizontal_velocity_fps.get()),
                wind_speed_mph=float(self.wind_speed_mph.get())
            )

            parachutes = []

            for row in self.parachute_rows:
                chute = Parachutes(
                    name=row["name"].get(),
                    diameter_in=float(row["diameter"].get()),
                    cd=float(row["cd"].get()),
                    deploy_altitude_ft=float(row["deploy_altitude"].get()),
                    deploy_time_s=float(row["deploy_time"].get()),
                    deploy_at_apogee=row["deploy_at_apogee"].get(),
                    reefing_factor=float(row["reefing_factor"].get())
                )

                parachutes.append(chute)

            sim = ParachuteDescentSimulator(
                rocket=rocket,
                parachutes=parachutes
            )

            sim.simulate_descent()

            summary = sim.get_results_summary()
            plot_data = sim.get_plot_data()

            self.root.after(
                0,
                lambda: self.display_results(summary, plot_data)
            )

        except Exception as error:
            self.root.after(0, lambda error=error: self.handle_simulation_error(error))
    
    def handle_simulation_error(self, error):
        self.run_button.config(state="normal")
        self.output_text.insert(tk.END, f"\nError: {error}\n")
        messagebox.showerror("Error", str(error))

    def display_results(self, summary, plot_data):
        self.output_text.delete("1.0", tk.END)

        self.output_text.insert(tk.END, "=== PARACHUTE DESCENT SUMMARY ===\n\n")

        rocket = summary["rocket"]

        self.output_text.insert(
            tk.END,
            f"Mass: {rocket['mass_kg']:.2f} kg ({rocket['mass_lbs']:.1f} lbs)\n"
        )

        self.output_text.insert(
            tk.END,
            f"Apogee: {rocket['apogee_ft_agl']:,.0f} ft AGL\n\n"
        )

        self.output_text.insert(tk.END, "Parachutes:\n")

        for chute in summary["parachutes"]:
            deploy = chute["deployment"]
            full = chute["full_deployment"]
            shock = chute["shock"]

            deploy_time = f"{deploy['time_s']:.2f} s" if deploy["status"] else "N/A"
            deploy_velocity = f"{deploy['total_velocity_fps']:.1f} ft/s" if deploy["status"] else "N/A"

            full_time = f"{full['time_s']:.2f} s" if full["status"] else "N/A"
            full_velocity = f"{full['total_velocity_fps']:.1f} ft/s" if full["status"] else "N/A"

            shock_text = f"{shock['max_force_lbf']:.0f} lbf" if shock["status"] else "N/A"

            self.output_text.insert(
                tk.END,
                f"{chute['name']}: "
                f"{chute['diameter_in']:.0f} in, "
                f"deploy @ {chute['deploy_altitude_ft']:,.0f} ft, "
                f"deployed t={deploy_time}, "
                f"v={deploy_velocity}, "
                f"full t={full_time}, "
                f"full v={full_velocity}, "
                f"shock={shock_text}\n"
            )

        landing = summary["landing"]

        if landing["status"]:
            self.output_text.insert(tk.END, "\nLanding:\n")
            self.output_text.insert(tk.END, f"Time: {landing['time_s']:.2f} s\n")
            self.output_text.insert(
                tk.END,
                f"Vertical velocity: {landing['vertical_velocity_fps']:.1f} ft/s\n"
            )
            self.output_text.insert(
                tk.END,
                f"Horizontal velocity: {landing['horizontal_velocity_fps']:.1f} ft/s\n"
            )
            self.output_text.insert(
                tk.END,
                f"Total velocity: {landing['total_velocity_fps']:.1f} ft/s\n"
            )

        print("Plot data length:", len(plot_data["time_s"]))
        self.plot_panel.update(plot_data)
        self.run_button.config(state="normal")

    def create_plot_area(self):
        self.plot_frame = ttk.LabelFrame(self.plot_tab, text="Simulation Plots")
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.plot_panel = RecoveryPlotPanel(self.plot_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecoverySimulatorGUI(root)
    root.mainloop()