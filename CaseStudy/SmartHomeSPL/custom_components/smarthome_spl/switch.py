"""Simulated switches for SmartHome SPL."""
from __future__ import annotations
import logging
from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up simulated switches for the active SPL variant."""
    entities = []

    #if[Alarm]
    try:
        entities.append(AlarmSirenSwitch("Home Alarm Siren", "alarm_siren"))
        _LOGGER.debug("[Alarm] Added siren switch")
    except Exception as err:
        _LOGGER.exception("[Alarm] Failed to create siren switch: %s", err)
    #endif

    if entities:
        async_add_entities(entities, True)


#if[Alarm]
class AlarmSirenSwitch(SwitchEntity):
    """Simulated alarm siren switch."""

    def __init__(self, name: str, unique: str):
        self._attr_name: str = name
        self._attr_unique_id: str = f"smarthome_spl_switch_{unique}"
        self._attr_is_on: bool = False
        # ✅ entity_id stable
        self.entity_id = f"switch.{unique}"

    @property
    def icon(self) -> str:
        return "mdi:alarm-bell" if self._attr_is_on else "mdi:alarm-off"

    async def async_turn_on(self, **kwargs):
        self._attr_is_on = True
        _LOGGER.debug("[Alarm] Siren ON")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False
        _LOGGER.debug("[Alarm] Siren OFF")
        self.async_write_ha_state()
#endif
