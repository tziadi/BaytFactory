"""Simulated door binary sensor for SmartHome SPL."""
from __future__ import annotations
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the door binary sensor if feature is enabled."""
    entities = []

    #if[Door]
    try:
        door_entity = DoorContact("Front Door", "front_door")
        entities.append(door_entity)
        _LOGGER.debug("[Door] Added Front Door binary_sensor")
    except Exception as err:
        _LOGGER.exception("[Door] Failed to create DoorContact: %s", err)
    #endif

    if entities:
        async_add_entities(entities, True)


#if[Door]
class DoorContact(BinarySensorEntity):
    """Simulated door contact sensor entity."""

    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, name: str, unique: str):
        self._attr_name = name
        self._open = False
        self._attr_unique_id = f"smarthome_spl_binary_sensor_{unique}"
        # ✅ entity_id stable, cohérent avec Lovelace
        self.entity_id = f"binary_sensor.{unique}"

    @property
    def is_on(self) -> bool:
        """Return True if the door is open."""
        return self._open

    @property
    def extra_state_attributes(self):
        return {"friendly_status": "Closed" if not self._open else "Open"}

    async def async_set_state(self, open_state: bool):
        self._open = open_state
        _LOGGER.debug("[Door] Door %s", "opened" if open_state else "closed")
        self.async_write_ha_state()
#endif
