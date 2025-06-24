import random
from abc import ABC, abstractmethod

class Subsystem(ABC):
    @abstractmethod
    def update(self, time_step):
        pass

    @abstractmethod
    def status(self):
        pass

# altitude control subsystem
class AttitudeControlSystem(Subsystem):
    def __init__(self):
        self.orientation = 0.0
        self.drift_detected = False

    def induce_drift(self):
        self.drift_detected = True
        print("Attitude anomaly: Gyro drift detected!")

    def update(self, time_step):
        if self.drift_detected:
            self.orientation += 0.5  # larger drift
            print("Stabilizing orientation due to drift...")
            self.drift_detected = False  # assume corrected
        else:
            self.orientation += 0.1

    def status(self):
        return f"Orientation: {self.orientation:.2f} deg"

# power System
class PowerSystem(Subsystem):
    def __init__(self):
        self.__battery_capacity = 100.0  # Wh
        self.__battery_level = 80.0      # Wh
        self.__solar_input = 50.0        # W
        self.orientation_adjusted = False

    def set_solar_input(self, power_watts):
        self.__solar_input = power_watts

    def adjust_orientation_for_solar(self):
        if not self.orientation_adjusted:
            self.__solar_input += 15  # simulate boost from solar
            self.orientation_adjusted = True
            print("Adjusted orientation to maximize solar input.")

    def reset_orientation_adjustment(self):
        self.orientation_adjusted = False

    def get_battery_level(self):
        return self.__battery_level

    def consume_power(self, watts, duration_s):
        energy_used = (watts * duration_s) / 3600
        self.__battery_level -= energy_used
        self.__battery_level = max(0, self.__battery_level)

    def supply_power(self, duration_s):
        energy_generated = (self.__solar_input * duration_s) / 3600
        self.__battery_level += energy_generated
        self.__battery_level = min(self.__battery_capacity, self.__battery_level)

    def update(self, time_step):
        self.supply_power(time_step)

    def status(self):
        return f"Battery: {self.__battery_level:.2f} Wh | Solar In: {self.__solar_input:.1f} W"

# payload: thermal camera subsystem
class PayloadCamera(Subsystem):
    def __init__(self):
        self.active = True
        self.temperature = 25.0
        self.fan_on = False
        self.overheated = False

    def induce_overheat(self):
        self.overheated = True
        print(" Payload anomaly: Overheating!")

    def update(self, time_step, power_system: PowerSystem):
        if self.active:
            base_power = 10
            if self.overheated:
                self.fan_on = True
                fan_power = 5
                power_system.consume_power(base_power + fan_power, time_step)
                self.temperature -= 0.2  # cooling
                print(" Fan activated to cool payload.")
                if self.temperature <= 30:
                    self.overheated = False
                    self.fan_on = False
            else:
                if power_system.get_battery_level() > 5:
                    power_system.consume_power(base_power, time_step)
                    self.temperature += 0.05
                else:
                    self.active = False

    def status(self):
        state = "ON" if self.active else "OFF"
        fan = " (Fan ON)" if self.fan_on else ""
        return f"State: {state}{fan} | Temp: {self.temperature:.1f}°C"

# communications subsystem
class CommSystem(Subsystem):
    def __init__(self):
        self.active = True

    def update(self, time_step, power_system: PowerSystem):
        if self.active:
            power_needed = 5
            if power_system.get_battery_level() > 2:
                power_system.consume_power(power_needed, time_step)
            else:
                self.active = False

    def status(self):
        return "Transmitting" if self.active else "Offline"

# event manager with anomalies and eclipse that affects power
class EventManager:
    def __init__(self):
        self.eclipse_start = 900    # 15 min
        self.eclipse_end = 1800     # 30 min
        self.last_anomaly_time = -300  # 1st anomaly at -5 min (0)
        self.anomaly_interval = 300    # anomaly every 5 minutes

    def in_eclipse(self, current_time):
        orbit_time = current_time % 5400
        return self.eclipse_start <= orbit_time <= self.eclipse_end

    def inject_random_anomalies(self, current_time, attitude_system, payload_system):
        if current_time - self.last_anomaly_time >= self.anomaly_interval:
            anomaly_type = random.choice(["attitude", "payload", None])
            if anomaly_type == "attitude":
                attitude_system.induce_drift()
            elif anomaly_type == "payload":
                payload_system.induce_overheat()
            self.last_anomaly_time = current_time

    def handle_events(self, power_system: PowerSystem, comm_system: CommSystem, payload_system: PayloadCamera):
        battery = power_system.get_battery_level()
        if battery < 5:
            comm_system.active = False
        if battery < 3:
            payload_system.active = False
        if battery < 20 and not power_system.orientation_adjusted:
            power_system.adjust_orientation_for_solar()