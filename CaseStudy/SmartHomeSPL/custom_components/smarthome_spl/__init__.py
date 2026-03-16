# spl-smarthome-generated-variants/variant1/custom_components/smarthome_spl/__init__.py
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
import logging, inspect

_LOGGER = logging.getLogger(__name__)
DOMAIN = "smarthome_spl"

async def async_setup(hass, config):
    async def _on_started(event):
        from . import dashboard as _dash
        _LOGGER.warning(
            "INIT LOADED FROM %s, DASH=%s, ensure_dashboard_once is coroutine=%s",
            __file__, getattr(_dash, "__file__", "?"),
            inspect.iscoroutinefunction(getattr(_dash, "ensure_dashboard_once", None)),
        )

        from .dashboard import ensure_dashboard_once
        await ensure_dashboard_once(hass)  # <- DOIT être 'await'

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_started)
    return True
