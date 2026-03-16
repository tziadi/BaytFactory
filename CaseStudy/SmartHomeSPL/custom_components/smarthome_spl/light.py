"""Simulated lights for SmartHome SPL."""
from __future__ import annotations
import logging
from homeassistant.components.light import LightEntity, ColorMode

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up SmartLight entities for the active SPL variant."""
    entities = []

    #if[SmartLight]
    try:
        lamp_a = SmartLight("Lamp A", "lamp_a")
        lamp_b = SmartLight("Lamp B", "lamp_b")
        entities.extend([lamp_a, lamp_b])
        _LOGGER.debug("[SmartLight] Added entities: %s", [e.entity_id for e in entities])
    except Exception as err:
        _LOGGER.exception("[SmartLight] Failed to create light entities: %s", err)
    #endif

    if entities:
        async_add_entities(entities, True)


#if[SmartLight]
class SmartLight(LightEntity):
    """A simulated on/off SmartLight entity."""

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, name: str, unique: str):
        self._attr_name = name
        self._attr_unique_id = f"smarthome_spl_light_{unique}"
        self._attr_is_on = False
        # ✅ entity_id stables
        self.entity_id = f"light.{unique}"

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        _LOGGER.debug("[SmartLight] Turning ON %s", self.name)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        _LOGGER.debug("[SmartLight] Turning OFF %s", self.name)
        self.async_write_ha_state()

    @property
    def icon(self):
        return "mdi:lightbulb-on" if self._attr_is_on else "mdi:lightbulb-off"
#endif
