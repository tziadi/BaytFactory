"""Network health sensors (simulated) for SmartHome SPL."""
from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up simulated network sensors for the active SPL variant."""
    sensors = []

    #if[Network]
    #if[MQTT]
    try:
        sensors.append(NetworkSensor("Network MQTT", "mqtt", "online"))
        _LOGGER.debug("[Network] Added MQTT sensor")
    except Exception as err:
        _LOGGER.exception("[Network] Failed to create MQTT sensor: %s", err)
    #endif

    #if[Zigbee]
    try:
        sensors.append(NetworkSensor("Network Zigbee", "zigbee", "online"))
        _LOGGER.debug("[Network] Added Zigbee sensor")
    except Exception as err:
        _LOGGER.exception("[Network] Failed to create Zigbee sensor: %s", err)
    #endif

    #if[WiFi]
    try:
        sensors.append(NetworkSensor("Network WiFi", "wifi", "online"))
        _LOGGER.debug("[Network] Added WiFi sensor")
    except Exception as err:
        _LOGGER.exception("[Network] Failed to create WiFi sensor: %s", err)
    #endif

    #if[ZWave]
    try:
        sensors.append(NetworkSensor("Network ZWave", "zwave", "online"))
        _LOGGER.debug("[Network] Added ZWave sensor")
    except Exception as err:
        _LOGGER.exception("[Network] Failed to create ZWave sensor: %s", err)
    #endif

    if sensors:
        async_add_entities(sensors, True)
        _LOGGER.info("[Network] Registered sensors: %s", [s.entity_id for s in sensors])
    #endif


#if[Network]
class NetworkSensor(SensorEntity):
    """Simulated network status sensor."""

    def __init__(self, name: str, net_type: str, status: str):
        self._attr_name: str = name
        self._attr_unique_id: str = f"smarthome_spl_network_{net_type}"
        self._attr_native_value: str = status
        self._net_type: str = net_type
        # ✅ entity_id forcé pour coller à Lovelace
        self.entity_id = f"sensor.smarthome_spl_network_{net_type}"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"network": self._net_type}

    @property
    def icon(self) -> str:
        return "mdi:check-network-outline" if self._attr_native_value == "online" else "mdi:close-network-outline"
#endif
