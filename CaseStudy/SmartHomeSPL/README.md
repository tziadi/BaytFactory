# BaytFactory Smart Home SPL (Corrected)

This version fixes SPL-level inconsistencies:
- `SmartThermostat` now requires `AirConditioner`.
- `AirConditioner` requires `MQTT`.
- Always generates an `ac_power_switch` when Thermostat or AC is active.
- Camera variant (`Door_SensorCamera`) explicitly requires WiFi (and ffmpeg).

This ensures every derived variant is executable in Home Assistant without manual patching.
