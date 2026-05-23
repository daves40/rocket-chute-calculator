import numpy as np
import pandas as pd
import math
import sys



class ParachuteDescentSimulator:
    def __init__(self, total_mass, parachutes:
        # Rocket specifications
        ##################### EDIT BELOW THIS #####################
        self.body1_mass = 20.8  # kg
        self.body1_length = 90  # inches
        self.body2_mass = 3.06  # kg
        self.body2_length = 20  # inches
        self.body3_mass = 85  # kg
        self.body3_length = 180  # inches

        # Parachute specifications
        self.parachute1_diameter = parachute1_d  # inches - drogue
        self.parachute2_diameter = parachute2_d  # inches - main at 3000ft
        self.parachute3_diameter = parachute3_d  # inches - main at 1200ft
        self.parachute4_diameter = parachute4_d # inches - main at ?ft


        # Deployment altitudes
        self.apogee = 10000  # feet
        self.deploy_altitude_2 = 5000  # feet
        self.deploy_altitude_3 = 3000  # feet
        self.deploy_altitude_4 = 1200 # feet THIS IS NOT AN ACTUAL VALUE PLEASE CHANGE

        # Deployment times
        self.deploy_time_1 = 1.8  # seconds
        self.deploy_time_2 = 1.8  # seconds
        self.deploy_time_3 = 2.3  # seconds
        self.deploy_time_4 = 2.3  # seconds

        # Parachute drag coefficient
        self.cd_1 = parachute1_cd
        self.cd_2 = parachute2_cd
        self.cd_3 = parachute3_cd
        self.cd_4 = parachute4_cd

        # Environmental conditions (deterministic)
        self.wind_speed = 15  # mph (base wind speed)
        self.initial_horizontal_velocity = 100  # ft/s (initial horizontal velocity at apogee)

        ##################### EDIT ABOVE THIS #####################

        # Physical constants
        self.g = 9.80665  # m/s²

        # Total mass (constant throughout descent)
        # self.total_mass = self.body1_mass + self.body2_mass + self.body3_mass  # 76.56 kg
        self.total_mass = total_mass
        # Convert units
        self._convert_units()

        # Results storage
        self.results = []
        self.events = {}

    def _convert_units(self):
        """Convert all units to SI"""
        # Altitude conversions
        self.apogee_m = self.apogee * 0.3048  # feet to meters
        self.deploy_altitude_2_m = self.deploy_altitude_2 * 0.3048
        self.deploy_altitude_3_m = self.deploy_altitude_3 * 0.3048
        self.deploy_altitude_4_m = self.deploy_altitude_4 * 0.3048

        # Wind speed conversion
        self.wind_speed_mps = self.wind_speed * 0.44704  # mph to m/s
        self.initial_horizontal_velocity_mps = self.initial_horizontal_velocity * 0.3048  # ft/s to m/s

        # Parachute area calculations
        self.parachute1_radius_m = (self.parachute1_diameter * 0.0254) / 2
        self.parachute2_radius_m = (self.parachute2_diameter * 0.0254) / 2
        self.parachute3_radius_m = (self.parachute3_diameter * 0.0254) / 2
        self.parachute4_radius_m = (self.parachute4_diameter * 0.0254) / 2


        self.parachute1_area = math.pi * self.parachute1_radius_m ** 2
        self.parachute2_area = math.pi * self.parachute2_radius_m ** 2
        self.parachute3_area = math.pi * self.parachute3_radius_m ** 2
        self.parachute4_area = math.pi * self.parachute4_radius_m ** 2

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

    def get_parachute_areas_and_forces(self, time, velocity, air_density, parachute2_full_deployed,
                                       parachute3_full_deployed, parachute4_full_deployed):
        """Calculate parachute areas and individual forces based on deployment status"""
        areas = {
            'parachute1': 0.0,
            'parachute2': 0.0,
            'parachute3': 0.0,
            'parachute4': 0.0
        }

        forces = {
            'parachute1': 0.0,
            'parachute2': 0.0,
            'parachute3': 0.0,
            'parachute4': 0.0
        }

        # Parachute 1 (drogue) - deployed at apogee
        if time >= 0:  # Start immediately at t=0
            elapsed_time = time
            if elapsed_time >= 0:
                deploy_progress_1 = min(1.0, elapsed_time / self.deploy_time_1)
                # Most inflation happens at the end (use exponential model)
                effective_area_1 = self.parachute1_area * (1 - math.exp(-5 * deploy_progress_1))

                # Load sharing logic - maintain significant contribution
                if parachute4_full_deployed:
                    # When parachute 2 is fully deployed, drogue still contributes
                    effective_area_1 *= 0.5  # Keep 70% effectiveness
                elif parachute3_full_deployed:
                    # When parachute 3 is fully deployed, drogue still contributes substantially
                    effective_area_1 *= 0.5  # Keep 70% effectiveness
                elif parachute2_full_deployed:
                    # When parachute 2 is fully deployed, drogue still contributes
                    effective_area_1 *= 0.5  # Keep 70% effectiveness

                areas['parachute1'] = effective_area_1
                forces['parachute1'] = self.calculate_parachute_drag_force(velocity, air_density, effective_area_1,
                                                                           self.cd_1)

        # Parachute 2 (main at 3000ft) - starts at deployment time
        if hasattr(self, 'parachute2_deploy_start_time') and self.parachute2_deploy_start_time is not None:
            elapsed_time = time - self.parachute2_deploy_start_time
            if elapsed_time >= 0:
                deploy_progress_2 = min(1.0, elapsed_time / self.deploy_time_2)
                # Most inflation happens at the end (use exponential model)
                effective_area_2 = self.parachute2_area * (1 - math.exp(-5 * deploy_progress_2))

                # Load sharing logic - maintain significant contribution
                if parachute4_full_deployed:
                    # When parachute 2 is fully deployed, drogue still contributes
                    effective_area_2 *= 0.5  # Keep 50% effectiveness
                elif parachute3_full_deployed:
                    # When parachute 3 is fully deployed, parachute 2 still contributes
                    effective_area_2 *= 0.5  # Keep 50% effectiveness

                areas['parachute2'] = effective_area_2
                forces['parachute2'] = self.calculate_parachute_drag_force(velocity, air_density, effective_area_2,
                                                                           self.cd_2)

        # Parachute 3 (main at 1200ft) - starts at deployment time
        if hasattr(self, 'parachute3_deploy_start_time') and self.parachute3_deploy_start_time is not None:
            elapsed_time = time - self.parachute3_deploy_start_time
            if elapsed_time >= 0:
                deploy_progress_3 = min(1.0, elapsed_time / self.deploy_time_3)
                # Most inflation happens at the end (use exponential model)
                effective_area_3 = self.parachute3_area * (1 - math.exp(-5 * deploy_progress_3))
                areas['parachute3'] = effective_area_3
                forces['parachute3'] = self.calculate_parachute_drag_force(velocity, air_density, effective_area_3,
                                                                           self.cd_3)
                if parachute4_full_deployed:
                    # When parachute 2 is fully deployed, drogue still contributes
                    effective_area_3 *= 0.5  # Keep 50% effectiveness

        return areas, forces

    def simulate_descent(self):
        """Run the complete descent simulation"""
        # Initial conditions at apogee
        altitude = self.apogee_m  # Start at apogee (meters)
        vertical_velocity = 0.1  # Small initial velocity m/s (positive downward)
        horizontal_velocity = self.initial_horizontal_velocity_mps  # Realistic initial horizontal velocity
        horizontal_position = 0.0
        time = 0.0

        # Track key events
        events = {
            'parachute1_deploy': {'time': 0.0, 'velocity': None, 'status': False},
            'parachute1_full': {'time': None, 'velocity': None, 'status': False},
            'parachute2_deploy': {'time': None, 'velocity': None, 'status': False},
            'parachute2_full': {'time': None, 'velocity': None, 'status': False},
            'parachute3_deploy': {'time': None, 'velocity': None, 'status': False},
            'parachute3_full': {'time': None, 'velocity': None, 'status': False},
            'parachute4_deploy': {'time': None, 'velocity': None, 'status': False},
            "parachute4_full": {"time": None, "velocity": None, "status": False},
            'landing': {'time': None, 'velocity': None, 'status': False}
        }

        # Store results
        results = []
        max_shock_loadings = {'parachute1': 0, 'parachute2': 0, 'parachute3': 0, 'parachute4': 0}

        # Track deployment times
        self.parachute1_deploy_start_time = 0.0
        self.parachute2_deploy_start_time = None
        self.parachute3_deploy_start_time = None
        self.parachute4_deploy_start_time = None

        # Track forces for shock loading calculation
        parachute1_forces = []
        parachute1_times = []
        parachute2_forces = []
        parachute2_times = []
        parachute3_forces = []
        parachute3_times = []
        parachute4_forces = []
        parachute4_times = []

        # Set up deployment tracking
        parachute1_started = True  # Starts immediately
        parachute2_started = False
        parachute3_started = False
        parachute4_started = False
        parachute1_completed = False
        parachute2_completed = False
        parachute3_completed = False
        parachute4_completed = False

        # Time integration
        dt = 0.01  # 0.01 second time steps for better accuracy

        # Wind profile - deterministic and steady
        base_wind_speed = self.wind_speed_mps

        # Small, steady variation in wind (more realistic than random noise)
        def get_wind_at_altitude(altitude_m, time):
            # Base wind with altitude-dependent variation
            altitude_factor = max(0.5, 1.0 - (altitude_m / self.apogee_m) * 0.5)  # Wind decreases with altitude
            # Small time-based variation (smooth, not random)
            time_variation = 0.1 * math.sin(time * 0.2)  # Small sinusoidal variation
            return base_wind_speed * altitude_factor + time_variation

        # Run simulation
        while altitude > 0 and time < 300:  # Max 300 seconds

            # Calculate air density at current altitude
            air_density = self.calculate_air_density(altitude)

            # Calculate wind at current altitude and time (deterministic)
            current_wind = get_wind_at_altitude(altitude, time)

            # Relative velocities
            v_vertical = vertical_velocity  # Positive downward
            v_horizontal = horizontal_velocity - current_wind  # Relative to air

            # Total velocity relative to air
            v_total = math.sqrt(v_vertical ** 2 + v_horizontal ** 2)
            if v_total < 0.1:
                v_total = 0.1

            # Calculate parachute areas and forces with proper load sharing
            areas, forces = self.get_parachute_areas_and_forces(time, v_total, air_density, parachute2_completed,
                                                                parachute3_completed, parachute4_completed)

            # Total drag force
            drag_force_total = forces['parachute1'] + forces['parachute2'] + forces['parachute3'] + forces['parachute4']

            # Forces
            weight = self.total_mass * self.g

            # Accelerations (F = ma)
            # Net force = weight - drag (positive downward)
            net_vertical_force = weight - drag_force_total
            if abs(v_horizontal) > 0.1:
                # Horizontal drag force opposes horizontal motion relative to air
                horizontal_drag_force = (forces['parachute1'] + forces['parachute2'] + forces['parachute3'] + forces['parachute4']) * (
                            abs(v_horizontal) / v_total)
                net_horizontal_force = -horizontal_drag_force * (1 if v_horizontal >= 0 else -1)
            else:
                net_horizontal_force = 0

            az = net_vertical_force / self.total_mass
            ax = net_horizontal_force / self.total_mass

            # Store current state
            results.append({
                'time': time,
                'altitude_ft': altitude / 0.3048,  # Convert to feet
                'vertical_velocity_fps': vertical_velocity * 3.28084,  # Convert to ft/s
                'horizontal_velocity_fps': horizontal_velocity * 3.28084,  # Convert to ft/s
                'current_wind_fps': current_wind * 3.28084,  # Convert to ft/s
                'total_velocity_fps': v_total * 3.28084,
                'horizontal_position_ft': horizontal_position * 3.28084,
                'drag_force_N': drag_force_total,
                'drag_force_1_N': forces['parachute1'],
                'drag_force_2_N': forces['parachute2'],
                'drag_force_3_N': forces['parachute3'],
                'net_vertical_force_N': net_vertical_force
            })

            # Track forces during deployment for shock loading calculation
            if parachute1_started and not parachute1_completed:
                parachute1_forces.append(forces['parachute1'])
                parachute1_times.append(time)
            elif parachute2_started and not parachute2_completed:
                parachute2_forces.append(forces['parachute2'])
                parachute2_times.append(time)
            elif parachute3_started and not parachute3_completed:
                parachute3_forces.append(forces['parachute3'])
                parachute3_times.append(time)
            elif parachute4_started and not parachute4_completed:
                parachute4_forces.append(forces['parachute4'])
                parachute4_times.append(time)

            # Check for specific events
            altitude_ft = altitude / 0.3048

            # Record velocity 0.1s after parachute 1 start
            if abs(time - 0.1) < 0.005 and not events['parachute1_deploy']['status']:
                events['parachute1_deploy']['velocity'] = {
                    'vertical_fps': vertical_velocity * 3.28084,
                    'horizontal_fps': horizontal_velocity * 3.28084,
                    'total_fps': math.sqrt((vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                }
                events['parachute1_deploy']['status'] = True

            # Parachute 1 full deployment
            if parachute1_started and not parachute1_completed:
                if time >= (self.parachute1_deploy_start_time + self.deploy_time_1):
                    parachute1_completed = True
                    events['parachute1_full']['time'] = time
                    events['parachute1_full']['velocity'] = {
                        'vertical_fps': vertical_velocity * 3.28084,
                        'horizontal_fps': horizontal_velocity * 3.28084,
                        'total_fps': math.sqrt(
                            (vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                    }
                    events['parachute1_full']['status'] = True

            # Parachute 2 deployment (at 5000 ft)
            if altitude_ft <= self.deploy_altitude_2 and not parachute2_started:
                self.parachute2_deploy_start_time = time
                parachute2_started = True
                events['parachute2_deploy']['time'] = time
                events['parachute2_deploy']['velocity'] = {
                    'vertical_fps': vertical_velocity * 3.28084,
                    'horizontal_fps': horizontal_velocity * 3.28084,
                    'total_fps': math.sqrt((vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                }
                events['parachute2_deploy']['status'] = True

            # Parachute 2 full deployment
            if parachute2_started and not parachute2_completed:
                if time >= (self.parachute2_deploy_start_time + self.deploy_time_2):
                    parachute2_completed = True
                    events['parachute2_full']['time'] = time
                    events['parachute2_full']['velocity'] = {
                        'vertical_fps': vertical_velocity * 3.28084,
                        'horizontal_fps': horizontal_velocity * 3.28084,
                        'total_fps': math.sqrt(
                            (vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                    }
                    events['parachute2_full']['status'] = True

            # Parachute 3 deployment (at 3000 ft)
            if altitude_ft <= self.deploy_altitude_3 and not parachute3_started:
                self.parachute3_deploy_start_time = time
                parachute3_started = True
                events['parachute3_deploy']['time'] = time
                events['parachute3_deploy']['velocity'] = {
                    'vertical_fps': vertical_velocity * 3.28084,
                    'horizontal_fps': horizontal_velocity * 3.28084,
                    'total_fps': math.sqrt((vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                }
                events['parachute3_deploy']['status'] = True

            # Parachute 3 full deployment
            if parachute3_started and not parachute3_completed:
                if time >= (self.parachute3_deploy_start_time + self.deploy_time_3):
                    parachute3_completed = True
                    events['parachute3_full']['time'] = time
                    events['parachute3_full']['velocity'] = {
                        'vertical_fps': vertical_velocity * 3.28084,
                        'horizontal_fps': horizontal_velocity * 3.28084,
                        'total_fps': math.sqrt(
                            (vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                    }
                    events['parachute3_full']['status'] = True

            # Parachute 4 deployment (at 1200 ft)
            if altitude_ft <= self.deploy_altitude_4 and not parachute4_started:
                self.parachute4_deploy_start_time = time
                parachute4_started = True
                events['parachute4_deploy']['time'] = time
                events['parachute4_deploy']['velocity'] = {
                    'vertical_fps': vertical_velocity * 3.28084,
                    'horizontal_fps': horizontal_velocity * 3.28084,
                    'total_fps': math.sqrt((vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                }
                events['parachute4_deploy']['status'] = True

            # Parachute 4 full deployment
            if parachute4_started and not parachute4_completed:
                if time >= (self.parachute4_deploy_start_time + self.deploy_time_4):
                    parachute4_completed = True
                    events['parachute4_full']['time'] = time
                    events['parachute4_full']['velocity'] = {
                        'vertical_fps': vertical_velocity * 3.28084,
                        'horizontal_fps': horizontal_velocity * 3.28084,
                        'total_fps': math.sqrt(
                            (vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                    }
                    events['parachute4_full']['status'] = True

            # Landing condition
            if altitude <= 0:
                events['landing']['time'] = time
                events['landing']['velocity'] = {
                    'vertical_fps': vertical_velocity * 3.28084,
                    'horizontal_fps': horizontal_velocity * 3.28084,
                    'total_fps': math.sqrt((vertical_velocity * 3.28084) ** 2 + (horizontal_velocity * 3.28084) ** 2)
                }
                events['landing']['status'] = True
                break

            # Numerical integration (Euler method)
            vertical_velocity += az * dt
            horizontal_velocity += ax * dt
            altitude -= vertical_velocity * dt  # Subtract because positive velocity means falling down
            horizontal_position += horizontal_velocity * dt

            # Ensure altitude doesn't go negative
            altitude = max(altitude, 0)

            time += dt

        # Calculate maximum shock loadings with corrected methodology
        def calculate_max_shock_loading(forces, times):
            if len(forces) < 20:
                return 0

            max_shock = 0
            # Calculate shock loading as maximum rate of change using larger time intervals
            for i in range(1, len(forces) - 1):
                # Use 0.1 second intervals to smooth out small variations
                force_change = abs(forces[i + 1] - forces[i - 1])
                time_change = times[i + 1] - times[i - 1]
                if time_change > 0.01:  # Minimum time interval
                    shock_loading = force_change / time_change
                    max_shock = max(max_shock, shock_loading)

            # Scale to get realistic values
            return max_shock * 1.0  # Scaling factor

        max_shock_loadings['parachute1'] = calculate_max_shock_loading(parachute1_forces, parachute1_times)
        max_shock_loadings['parachute2'] = calculate_max_shock_loading(parachute2_forces, parachute2_times)
        max_shock_loadings['parachute3'] = calculate_max_shock_loading(parachute3_forces, parachute3_times)
        max_shock_loadings['parachute4'] = calculate_max_shock_loading(parachute4_forces, parachute4_times)

        # Store results
        self.results = results
        self.events = events
        self.max_shock_loadings = max_shock_loadings

        return results, events, max_shock_loadings

    def print_results(self):
        """Print the simulation results"""
        print("=== PARACHUTE DESCENT SIMULATION RESULTS ===")
        print(f"Total Rocket Mass: {self.total_mass:.2f} kg ({self.total_mass * 2.20462:.1f} lbs)")
        print(f"Apogee: {self.apogee:,} feet")
        print(f"Initial horizontal velocity: {self.initial_horizontal_velocity} ft/s")
        print()

        # Parachute 1 (Small-Drogue) results
        print(f"--- PARACHUTE 1 ({self.parachute1_diameter}\" SMAll-DROGUE) ---")
        print(f"Deployment altitude: {self.apogee:,} feet")
        print(f"Deployment time: {self.deploy_time_1} seconds")
        if self.events['parachute1_deploy']['velocity']:
            v = self.events['parachute1_deploy']['velocity']
            print(f"Velocity 0.1s after deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.events['parachute1_full']['velocity']:
            v = self.events['parachute1_full']['velocity']
            print(f"Velocity after full deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.max_shock_loadings['parachute1'] > 0:
            shock_lbf = self.max_shock_loadings['parachute1'] * 0.224809  # Convert N to lbf
            print(f"Maximum shock loading: {shock_lbf:.0f} lbf")
        print()

        # Parachute 2 (Big-Drogue at 5000ft) results
        print(f"--- PARACHUTE 2 ({self.parachute2_diameter}\" BIG-DROGUE at 5000ft) ---")
        print(f"Deployment altitude: {self.deploy_altitude_2:,} feet")
        print(f"Deployment time: {self.deploy_time_2} seconds")
        if self.events['parachute2_deploy']['velocity']:
            v = self.events['parachute2_deploy']['velocity']
            print(f"Velocity at deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.events['parachute2_full']['velocity']:
            v = self.events['parachute2_full']['velocity']
            print(f"Velocity after full deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.max_shock_loadings['parachute2'] > 0:
            shock_lbf = self.max_shock_loadings['parachute2'] * 0.224809  # Convert N to lbf
            print(f"Maximum shock loading: {shock_lbf:.0f} lbf")
        print()

        # Parachute 3 (Main at 3000ft) results
        print(f"--- PARACHUTE 3 ({self.parachute3_diameter}\" SMALL-MAIN at 3000ft) ---")
        print(f"Deployment altitude: {self.deploy_altitude_3:,} feet")
        print(f"Deployment time: {self.deploy_time_3} seconds")
        if self.events['parachute3_deploy']['velocity']:
            v = self.events['parachute3_deploy']['velocity']
            print(f"Velocity at deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.events['parachute3_full']['velocity']:
            v = self.events['parachute3_full']['velocity']
            print(f"Velocity after full deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.max_shock_loadings['parachute3'] > 0:
            shock_lbf = self.max_shock_loadings['parachute3'] * 0.224809  # Convert N to lbf
            print(f"Maximum shock loading: {shock_lbf:.0f} lbf")
        print()

        # Parachute 4 (Main at 1200ft) results
        print(f"--- PARACHUTE 4 ({self.parachute4_diameter}\" MAIN at 1200ft) ---")
        print(f"Deployment altitude: {self.deploy_altitude_4:,} feet")
        print(f"Deployment time: {self.deploy_time_4} seconds")
        if self.events['parachute4_deploy']['velocity']:
            v = self.events['parachute4_deploy']['velocity']
            print(f"Velocity at deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.events['parachute4_full']['velocity']:
            v = self.events['parachute4_full']['velocity']
            print(f"Velocity after full deployment:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")

        if self.max_shock_loadings['parachute4'] > 0:
            shock_lbf = self.max_shock_loadings['parachute4'] * 0.224809  # Convert N to lbf
            print(f"Maximum shock loading: {shock_lbf:.0f} lbf")
        print()

        # Landing results
        print("--- LANDING ---")
        if self.events['landing']['velocity']:
            v = self.events['landing']['velocity']
            print(f"Velocity upon landing:")
            print(f"  Vertical: {v['vertical_fps']:.1f} ft/s")
            print(f"  Horizontal: {v['horizontal_fps']:.1f} ft/s")
            print(f"  Total: {v['total_fps']:.1f} ft/s")
        print()
        # Validation check
        print("=== VALIDATION CHECK ===")
        if self.events['parachute1_full']['velocity']:
            final_velocity = self.events['parachute1_full']['velocity']['total_fps']
            if self.max_shock_loadings['parachute1'] > 0:
                shock_lbf = self.max_shock_loadings['parachute1'] * 0.224809
                print(f"Drogue parachute validation:")
                print(f"  Final velocity: {final_velocity:.0f} ft/s (expected: 60-80 ft/s)")
                print(f"  Shock loading: {shock_lbf:.0f} lbf (expected: 500-1000 lbf)")
        print()

    def save_csv_results(self, filename='parachute_descent_simulation.csv'):
        """Save detailed results to CSV file"""
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Full descent data saved to {filename}")
        print(f"Total data points: {len(df)}")
        return df


parachute_config1 = ParachuteDescentSimulator(90, 48, 60, 96, 120,2.2, 2.2, 2.2, 2.2)
results, events, shock_loadings = parachute_config1.simulate_descent()
parachute_config1.print_results()
df = parachute_config1.save_csv_results()
print("=== ADDITIONAL ANALYSIS ===")
max_altitude = df['altitude_ft'].max()
landing_time = df['time'].max()
max_vertical_velocity = df['vertical_velocity_fps'].abs().max()
max_total_velocity = df['total_velocity_fps'].max()
final_horizontal_velocity = df.iloc[-1]['horizontal_velocity_fps']
final_vertical_velocity = df.iloc[-1]['vertical_velocity_fps']
final_total_velocity = df.iloc[-1]['total_velocity_fps']

print(f"Maximum altitude reached: {max_altitude:,.0f} feet")
print(f"Total descent time: {landing_time:.1f} seconds")
print(f"Maximum vertical velocity: {max_vertical_velocity:.1f} ft/s")
print(f"Maximum total velocity: {max_total_velocity:.1f} ft/s")
print(f"Final horizontal velocity: {final_horizontal_velocity:.1f} ft/s")
print(f"Final vertical velocity: {final_vertical_velocity:.1f} ft/s")
print(f"Final total velocity: {final_total_velocity:.1f} ft/s")

#48, 60 (5000ft), 96 (3000ft), 120 (1200ft)