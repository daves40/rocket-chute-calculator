import numpy as np
import pandas as pd
import math


class Parachute:
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

        # Rocket specifications
        ##################### EDIT BELOW THIS #####################

        self.name = name
        self.diameter_in = diameter_in
        self.cd = cd
        self.deploy_altitude_ft = deploy_altitude_ft
        self.deploy_time_s = deploy_time_s
        self.deploy_at_apogee = deploy_at_apogee
        self.reefing_factor = reefing_factor

        self.deploy_start_time = None
        self.started = False
        self.completed = False

        self.area_m2 = self.calculate_area()
        self.force_history = []
        self.time_history = []