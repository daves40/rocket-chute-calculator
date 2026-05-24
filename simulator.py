import math

class ParachuteDescentSimulator:
    def __init__(self, rocket, parachutes):
        self.rocket = rocket
        self.parachutes = parachutes

        self.g = 9.80665

        self.results = []
        self.events = {}
        self.shock_results = {}
    
    def calculate_air_density(self, altitude_m):
        """Calculate air density at given altitude using standard atmosphere model"""
        # Standard atmosphere model
        lapse_rate = 0.0065  # Temperature lapse rate (K/m)
        sea_level_temp = 288.15  # Sea level standard temperature (K)
        sea_level_pressure = 101325  # Sea level standard pressure (Pa)
        gas_constant = 287.053  # Gas constant for air (J/(kg·K))

        # Calculate temperature at altitude
        temperature = sea_level_temp - lapse_rate * altitude_m

        # Prevent temperature from going below absolute zero
        if temperature < 180:
            temperature = 180

        # Calculate pressure at altitude
        try:
            pressure = sea_level_pressure * (1 - (lapse_rate * altitude_m) / sea_level_temp) ** (
                        self.g / (gas_constant * lapse_rate))
        except:
            pressure = sea_level_pressure * math.exp(-self.g * altitude_m / (gas_constant * sea_level_temp))

        # Calculate air density
        try:
            air_density = pressure / (gas_constant * temperature)
        except:
            air_density = 1.225  # Default sea level density

        return max(air_density, 0.01)

    def calculate_parachute_drag_force(self, velocity, air_density, area, cd):
        """Calculate drag force: F = 0.5 * rho * v² * Cd * A"""
        if velocity < 0.1 or area <= 0:
            return 0.0
        return 0.5 * air_density * velocity ** 2 * cd * area

    def get_parachute_areas_and_forces(self, time, velocity, air_density):
        areas = {}
        forces = {}

        for i, chute in enumerate(self.parachutes):
            areas[chute.name] = 0.0
            forces[chute.name] = 0.0

            if not chute.started:
                continue

            effective_area = chute.effective_area(time)

            later_chutes = self.parachutes[i + 1:]

            later_chute_completed = any(
                later_chute.completed for later_chute in later_chutes
            )

            # Load sharing logic 
            if later_chute_completed:
                effective_area *= chute.reefing_factor

            areas[chute.name] = effective_area

            forces[chute.name] = self.calculate_parachute_drag_force(
                velocity,
                air_density,
                effective_area,
                chute.cd
            )

        return areas, forces


    def simulate_descent(self):
        altitude = self.rocket.apogee_m
        vertical_velocity = 0.1
        horizontal_velocity = self.rocket.initial_horizontal_velocity_mps
        horizontal_position = 0.0
        time = 0.0
        dt = 0.01

        results = []
        events = {}

        for chute in self.parachutes:
            events[f"{chute.name}_deploy"] = {
                "time": None,
                "velocity": None,
                "status": False
            }

            events[f"{chute.name}_full"] = {
                "time": None,
                "velocity": None,
                "status": False
            }

        events["landing"] = {
            "time": None,
            "velocity": None,
            "status": False
        }

        base_wind_speed = self.rocket.wind_speed_mps

        def get_wind_at_altitude(altitude_m, time):
            altitude_factor = max(0.5, 1.0 - (altitude_m / self.rocket.apogee_m) * 0.5)
            time_variation = 0.1 * math.sin(time * 0.2)
            return base_wind_speed * altitude_factor + time_variation

        def velocity_snapshot():
            vertical_fps = vertical_velocity * 3.28084
            horizontal_fps = horizontal_velocity * 3.28084
            total_fps = math.sqrt(vertical_fps ** 2 + horizontal_fps ** 2)

            return {
                "vertical_fps": vertical_fps,
                "horizontal_fps": horizontal_fps,
                "total_fps": total_fps
            }

        while altitude > 0 and time < 300:
            air_density = self.calculate_air_density(altitude)
            current_wind = get_wind_at_altitude(altitude, time)

            v_vertical = vertical_velocity
            v_horizontal = horizontal_velocity - current_wind

            v_total = math.sqrt(v_vertical ** 2 + v_horizontal ** 2)

            if v_total < 0.1:
                v_total = 0.1

            altitude_ft = altitude / 0.3048

            # Check deployment for each parachute
            for chute in self.parachutes:
                if chute.should_deploy(altitude_ft, time):
                    chute.started = True
                    chute.deploy_start_time = time

                    events[f"{chute.name}_deploy"]["time"] = time
                    events[f"{chute.name}_deploy"]["velocity"] = velocity_snapshot()
                    events[f"{chute.name}_deploy"]["status"] = True

            # Check full deployment for each parachute
            for chute in self.parachutes:
                if chute.started and not chute.completed:
                    if time >= chute.deploy_start_time + chute.deploy_time_s:
                        chute.completed = True

                        events[f"{chute.name}_full"]["time"] = time
                        events[f"{chute.name}_full"]["velocity"] = velocity_snapshot()
                        events[f"{chute.name}_full"]["status"] = True

            # Calculate parachute forces
            areas, forces = self.get_parachute_areas_and_forces(
                time,
                v_total,
                air_density
            )

            drag_force_total = sum(forces.values())

            weight = self.rocket.total_mass_kg * self.g

            if v_total > 0.1:
                vertical_drag_force = drag_force_total * (v_vertical / v_total)
                horizontal_drag_force = drag_force_total * (v_horizontal / v_total)
            else:
                vertical_drag_force = 0.0
                horizontal_drag_force = 0.0

            net_vertical_force = weight - vertical_drag_force
            net_horizontal_force = -horizontal_drag_force

            az = net_vertical_force / self.rocket.total_mass_kg
            ax = net_horizontal_force / self.rocket.total_mass_kg

            row = {
                "time": time,
                "altitude_ft": altitude / 0.3048,
                "vertical_velocity_fps": vertical_velocity * 3.28084,
                "horizontal_velocity_fps": horizontal_velocity * 3.28084,
                "current_wind_fps": current_wind * 3.28084,
                "total_velocity_fps": v_total * 3.28084,
                "horizontal_position_ft": horizontal_position * 3.28084,
                "drag_force_N": drag_force_total,
                "vertical_drag_force_N": vertical_drag_force,
                "horizontal_drag_force_N": horizontal_drag_force,
                "weight_N": weight,
                "net_vertical_force_N": net_vertical_force,
                "net_horizontal_force_N": net_horizontal_force
            }

            for chute in self.parachutes:
                row[f"{chute.name}_drag_force_N"] = forces[chute.name]
                row[f"{chute.name}_area_m2"] = areas[chute.name]

            results.append(row)

            # Track shock loading data
            for chute in self.parachutes:
                if chute.started and not chute.completed:
                    chute.force_history.append(forces[chute.name])
                    chute.time_history.append(time)

            # Landing condition
            if altitude <= 0:
                events["landing"]["time"] = time
                events["landing"]["velocity"] = velocity_snapshot()
                events["landing"]["status"] = True
                break

            vertical_velocity += az * dt
            horizontal_velocity += ax * dt

            altitude -= vertical_velocity * dt
            horizontal_position += horizontal_velocity * dt

            if altitude <= 0:
                altitude = 0

                events["landing"]["time"] = time
                events["landing"]["velocity"] = velocity_snapshot()
                events["landing"]["status"] = True
                break

            time += dt

        def calculate_max_shock_load(forces):
            """Return maximum deployment force in Newtons."""
            if len(forces) == 0:
                return 0.0

            return max(forces)


        def calculate_max_force_ramp_rate(forces, times):
            """Return maximum force ramp rate in N/s."""
            if len(forces) < 3:
                return 0.0

            max_ramp_rate = 0.0

            for i in range(1, len(forces) - 1):
                force_change = abs(forces[i + 1] - forces[i - 1])
                time_change = times[i + 1] - times[i - 1]

                if time_change > 0:
                    ramp_rate = force_change / time_change
                    max_ramp_rate = max(max_ramp_rate, ramp_rate)

            return max_ramp_rate


        shock_results = {}

        for chute in self.parachutes:
            max_force_N = calculate_max_shock_load(chute.force_history)
            max_force_lbf = max_force_N * 0.224809

            max_ramp_rate_N_per_s = calculate_max_force_ramp_rate(
                chute.force_history,
                chute.time_history
            )

            shock_results[chute.name] = {
                "max_force_N": max_force_N,
                "max_force_lbf": max_force_lbf,
                "max_force_ramp_rate_N_per_s": max_ramp_rate_N_per_s
            }

        self.results = results
        self.events = events
        self.shock_results = shock_results

        return results, events, shock_results

    def print_results(self):
        print("=== PARACHUTE DESCENT SUMMARY ===")
        print(f"Mass: {self.rocket.total_mass_kg:.2f} kg ({self.rocket.total_mass_kg * 2.20462:.1f} lbs)")
        print(f"Apogee: {self.rocket.apogee_ft:,.0f} ft (AGL)")
        print()

        print("Parachutes:")
        for chute in self.parachutes:
            deploy_key = f"{chute.name}_deploy"
            full_key = f"{chute.name}_full"

            deploy_event = self.events[deploy_key]
            full_event = self.events[full_key]

            if deploy_event["status"]:
                deploy_time = f"{deploy_event['time']:.2f} s"
                deploy_velocity = f"{deploy_event['velocity']['total_fps']:.1f} ft/s"
            else:
                deploy_time = "N/A"
                deploy_velocity = "N/A"

            if full_event["status"]:
                full_time = f"{full_event['time']:.2f} s"
                full_velocity = f"{full_event['velocity']['total_fps']:.1f} ft/s"
            else:
                full_time = "N/A"
                full_velocity = "N/A"

            if chute.name in self.shock_results:
                shock_lbf = self.shock_results[chute.name]["max_force_lbf"]
                shock_text = f"{shock_lbf:.0f} lbf"
            else:
                shock_text = "N/A"

            print(
                f"{chute.name}: "
                f"{chute.diameter_in:.0f} in, "
                f"deploy @ {chute.deploy_altitude_ft:,.0f} ft, "
                f"deployed t={deploy_time}, "
                f"v={deploy_velocity}, "
                f"full t={full_time}, "
                f"full v={full_velocity}, "
                f"shock={shock_text}"
            )

        print()

        if self.events["landing"]["status"]:
            landing = self.events["landing"]
            v = landing["velocity"]

            print("Landing:")
            print(f"Time: {landing['time']:.2f} s")
            print(f"Vertical velocity: {v['vertical_fps']:.1f} ft/s")
            print(f"Horizontal velocity: {v['horizontal_fps']:.1f} ft/s")
            print(f"Total velocity: {v['total_fps']:.1f} ft/s")