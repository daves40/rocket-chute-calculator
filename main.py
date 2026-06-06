from parachutes import Parachutes
from simulator import ParachuteDescentSimulator
from rocket import Rocket

rocket = Rocket(
    name="STAR Rocket",
    total_mass_kg=90,
    apogee_ft=10000,
    launch_site_elevation_ft=2000,
    initial_horizontal_velocity_fps=100,
    wind_speed_mph=15
)

parachute_config = [
    Parachutes(
        name="Small Drogue",
        diameter_in=48,
        cd=2.2,
        deploy_altitude_ft=10000,
        deploy_time_s=1.8,
        deploy_at_apogee=True,
        reefing_factor=0.5
    ),
    Parachutes(
        name="Big Drogue",
        diameter_in=60,
        cd=2.2,
        deploy_altitude_ft=5000,
        deploy_time_s=1.8,
        reefing_factor=0.5
    ),
    Parachutes(
        name="Small Main",
        diameter_in=96,
        cd=2.2,
        deploy_altitude_ft=3000,
        deploy_time_s=2.3,
        reefing_factor=0.5
    ),
    Parachutes(
        name="Main",
        diameter_in=120,
        cd=2.2,
        deploy_altitude_ft=1200,
        deploy_time_s=2.3
    )
]

sim = ParachuteDescentSimulator(
    rocket=rocket,
    parachutes=parachute_config
)

sim.simulate_descent()

summary = sim.get_results_summary()

sim.print_results()