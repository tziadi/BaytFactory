import argparse
import asyncio
from pathlib import Path

from homeassistant.auth import auth_manager_from_config
from homeassistant.auth.const import GROUP_ID_ADMIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er


async def bootstrap_user(config_dir: str, username: str, password: str) -> str:
    hass = HomeAssistant(config_dir)
    await asyncio.gather(dr.async_load(hass), er.async_load(hass))
    hass.auth = await auth_manager_from_config(hass, [{"type": "homeassistant"}], [])
    provider = hass.auth.auth_providers[0]
    await provider.async_initialize()

    if provider.data is None:
        raise RuntimeError("Home Assistant auth provider failed to initialize")

    existing_user = None
    for user in provider.data.users:
        if user["username"] == username:
            existing_user = user
            break

    if existing_user is None:
        provider.data.add_auth(username, password)
        await provider.data.async_save()

    credentials = await provider.async_get_or_create_credentials({"username": username})
    user = await hass.auth.async_get_user_by_credentials(credentials)
    if user is None:
        user = await hass.auth.async_create_user(username, group_ids=[GROUP_ID_ADMIN])
        await hass.auth.async_link_user(user, credentials)

    await hass.auth._store._store.async_save(hass.auth._store._data_to_save())
    await hass.async_stop()
    return user.id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    config_dir = str(Path(args.config).resolve())
    user_id = asyncio.run(bootstrap_user(config_dir, args.username, args.password))
    print(user_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
