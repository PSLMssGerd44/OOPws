from subsystems import (
    AttitudeControlSystem,
    PowerSystem,
    PayloadCamera,
    CommSystem,
    EventManager
)

class Spacecraft:
    def __init__(self):
        self.time = 0  # in seconds
        self.attitude = AttitudeControlSystem()
        self.power = PowerSystem()
        self.payload = PayloadCamera()
        self.comm = CommSystem()
        self.event_manager = EventManager()

    def update(self, time_step):
        self.time += time_step

        # Eclipse event
        if self.event_manager.in_eclipse(self.time):
            self.power.set_solar_input(0)
            print(" Eclipse: No solar input.")
        else:
            if self.power.orientation_adjusted:
                self.power.reset_orientation_adjustment()
            self.power.set_solar_input(50)

        # random anomalies
        self.event_manager.inject_random_anomalies(
            self.time, self.attitude, self.payload
        )

        # update subsystems
        self.power.update(time_step)
        self.attitude.update(time_step)
        self.payload.update(time_step, self.power)
        self.comm.update(time_step, self.power)

        # handle anomalies for coms, payload and power
        self.event_manager.handle_events(self.power, self.comm, self.payload)

    def report_status(self):
        print(f"\n  Time: {self.time // 60} min {self.time % 60}s")
        print(f"[Power]   {self.power.status()}")
        print(f"[Attitude]{self.attitude.status()}")
        print(f"[Payload] {self.payload.status()}")
        print(f"[Comm]    {self.comm.status()}")
        print("-" * 40)

if __name__ == "__main__":
    sc = Spacecraft()
    print(" Spacecraft Simulation Starting...\n")

    for _ in range(60):  # simulate 1h in 60s  steps
        sc.update(time_step=60)
        sc.report_status()

    print("\n Simulation Complete.")