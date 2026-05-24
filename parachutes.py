import math

class Parachutes:
    def __init__(
            self, 
            name,
            diameter_in,
            cd,
            deploy_altitude_ft,
            deploy_time_s,
            deploy_at_apogee=False,
            reefing_factor=1.0
    ):
        # Chute paramters
        self.name = name
        self.diameter_in = diameter_in
        self.cd = cd
        self.deploy_altitude_ft = deploy_altitude_ft
        self.deploy_time_s = deploy_time_s
        self.deploy_at_apogee = deploy_at_apogee
        self.reefing_factor = reefing_factor

        # Deploy states
        self.deploy_start_time = None
        self.started = False
        self.completed = False

        # Data storage
        self.force_history = []
        self.time_history = []


        # Convert to SI units
        self.diameter_m = self.diameter_in * 0.0254
        self.radius_m = self.diameter_m / 2
        self.area_m2 = math.pi * self.radius_m ** 2
        self.deploy_altitude_m = self.deploy_altitude_ft * 0.3048
         
    def should_deploy(self, altitude_ft, time):
        if self.deploy_at_apogee:
            return time >= 0 and not self.started
        return altitude_ft <= self.deploy_altitude_ft and not self.started

    def deployment_progress(self, time):
        if self.deploy_start_time is None:
            return 0.0
        elapsed = time - self.deploy_start_time
        return min(1.0, max(0.0, elapsed / self.deploy_time_s))

    def effective_area(self, time):
        progress = self.deployment_progress(time)
        # Most inflation happens at the end (use exponential model)
        return self.area_m2 * (1 - math.exp(-5 * progress))
