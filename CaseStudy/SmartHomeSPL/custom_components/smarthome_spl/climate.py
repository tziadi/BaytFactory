"""Simulated climate entities for SmartHome SPL."""
from __future__ import annotations
import logging
import random
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import UnitOfTemperature

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup simulated climate devices if features are enabled."""
    entities = []

    #if[SmartThermostat]
    try:
        entities.append(SmartThermostat("Smart Thermostat", "smart_thermostat"))
        _LOGGER.debug("[SmartThermostat] Added Smart Thermostat climate entity")
    except Exception as err:
        _LOGGER.exception("[SmartThermostat] Failed to create SmartThermostat: %s", err)
    #endif

    #if[AirConditioner]
    try:
        entities.append(AirConditioner("Air Conditioner", "air_conditioner"))
        _LOGGER.debug("[AirConditioner] Added Air Conditioner climate entity")
    except Exception as err:
        _LOGGER.exception("[AirConditioner] Failed to create AirConditioner: %s", err)
    #endif

    if entities:
        async_add_entities(entities, True)
        _LOGGER.debug("[Climate] Entities added: %s", [e.entity_id for e in entities])


class _BaseClimate(ClimateEntity):
    """Base class for simulated climate entities."""

    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 16
    _attr_max_temp = 30

    def __init__(self, name: str, unique: str, current: float = 22.0, target: float = 22.0):
        self._attr_name = name
        self._attr_unique_id = f"smarthome_spl_climate_{unique}"
        self._attr_current_temperature = current
        self._attr_target_temperature = target
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
        self._attr_hvac_action = HVACAction.OFF
        # ✅ entity_id stable
        self.entity_id = f"climate.{unique}"

    async def async_set_temperature(self, **kwargs):
        if (t := kwargs.get("temperature")) is not None:
            self._attr_target_temperature = float(t)
            _LOGGER.debug("[%s] Target temperature set to %s°C", self.name, t)
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        self._attr_hvac_mode = hvac_mode
        _LOGGER.debug("[%s] HVAC mode set to %s", self.name, hvac_mode)
        self._update_action()
        self.async_write_ha_state()

    def _update_action(self):
        if self._attr_hvac_mode == HVACMode.HEAT:
            self._attr_hvac_action = HVACAction.HEATING if self._attr_current_temperature < self._attr_target_temperature else HVACAction.IDLE
        elif self._attr_hvac_mode == HVACMode.COOL:
            self._attr_hvac_action = HVACAction.COOLING if self._attr_current_temperature > self._attr_target_temperature else HVACAction.IDLE
        elif self._attr_hvac_mode == HVACMode.AUTO:
            self._attr_hvac_action = random.choice([HVACAction.HEATING, HVACAction.COOLING, HVACAction.IDLE])
        else:
            self._attr_hvac_action = HVACAction.OFF

    async def async_update(self):
        if self._attr_hvac_mode in (HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO):
            if self._attr_current_temperature < self._attr_target_temperature:
                self._attr_current_temperature += 0.1
            elif self._attr_current_temperature > self._attr_target_temperature:
                self._attr_current_temperature -= 0.1
        self._update_action()


#if[SmartThermostat]
class SmartThermostat(_BaseClimate):
    """Simulated Smart Thermostat."""
    pass
#endif


#if[AirConditioner]
class AirConditioner(_BaseClimate):
    """Simulated Air Conditioner."""
    pass
#endif
