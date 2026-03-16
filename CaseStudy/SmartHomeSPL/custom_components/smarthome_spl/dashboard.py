"""Dashboard generator for SmartHome SPL variants (async-safe)."""
from __future__ import annotations

import os
import logging
import shutil
from typing import Optional
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
DOMAIN = "smarthome_spl"


def _first_existing(*paths: str) -> Optional[str]:
    for p in paths:
        if os.path.exists(p):
            return p
    return None


async def ensure_dashboard_once(hass: HomeAssistant) -> None:
    """Copy/Create the dashboard exactly once (avoid duplicates)."""
    data = hass.data.setdefault(DOMAIN, {})
    if data.get("dashboard_done"):
        return
    data["dashboard_done"] = True
    await generate_dashboard(hass)


async def generate_dashboard(hass: HomeAssistant) -> None:
    """
    1) If lovelace_spl.yaml (or ui-lovelace_spl.yaml) exists -> copy to ui-lovelace.yaml
    2) Else, write a minimal dashboard to avoid a blank screen.
    All filesystem ops run in the executor (no blocking on the event loop).
    """
    config_dir = hass.config.path()
    src = _first_existing(
        os.path.join(config_dir, "lovelace_spl.yaml"),
        os.path.join(config_dir, "ui-lovelace_spl.yaml"),
    )
    target = os.path.join(config_dir, "ui-lovelace.yaml")

    await hass.async_add_executor_job(_write_dashboard_sync, src, target)


def _write_dashboard_sync(src: Optional[str], target: str) -> None:
    # Clean old target if exists
    try:
        if os.path.exists(target):
            os.remove(target)
    except Exception as e:
        _LOGGER.warning("[Dashboard] Could not remove existing ui-lovelace.yaml: %s", e)

    # Copy from source if present
    if src and os.path.exists(src):
        try:
            shutil.copyfile(src, target)
            _LOGGER.info("[Dashboard] ui-lovelace.yaml created from %s", os.path.basename(src))
            return
        except Exception as e:
            _LOGGER.exception("[Dashboard] Copy failed, falling back to minimal UI: %s", e)

    # Fallback minimal
    try:
        minimal = (
            "title: BaytFactory (auto)\n"
            "views:\n"
            "  - title: Main\n"
            "    path: main\n"
            "    icon: mdi:home\n"
            "    cards:\n"
            "      - type: markdown\n"
            "        content: |\n"
            "          ### ✅ Default dashboard\n"
            "          No `lovelace_spl.yaml` found; generated a minimal UI.\n"
        )
        with open(target, "w", encoding="utf-8") as f:
            f.write(minimal)
        _LOGGER.warning("[Dashboard] No lovelace_spl.yaml found. Generated minimal ui-lovelace.yaml")
    except Exception as e:
        _LOGGER.exception("[Dashboard] Failed to create fallback dashboard: %s", e)
