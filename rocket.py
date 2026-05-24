class Rocket:
    def __init__(
        self,
        name,
        total_mass_kg,
        apogee_ft,
        launch_site_elevation_ft=0,
        initial_horizontal_velocity_fps=100,
        wind_speed_mph=15
    ):
        self.name = name
        self.total_mass_kg = total_mass_kg

        # Altitude data
        self.apogee_ft = apogee_ft
        self.launch_site_elevation_ft = launch_site_elevation_ft

        # Motion/environment initial conditions
        self.initial_horizontal_velocity_fps = initial_horizontal_velocity_fps
        self.wind_speed_mph = wind_speed_mph

        # SI conversions
        self.apogee_m = self.apogee_ft * 0.3048
        self.launch_site_elevation_m = self.launch_site_elevation_ft * 0.3048
        self.initial_horizontal_velocity_mps = (
            self.initial_horizontal_velocity_fps * 0.3048
        )
        self.wind_speed_mps = self.wind_speed_mph * 0.44704