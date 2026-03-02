"""SBB Dashboard Cards integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BOOTSTRAP_ONLY,
    DEFAULT_BOOTSTRAP_ONLY,
    DOMAIN,
    SERVICE_GENERATE_FILES,
)
from .generator import async_generate_files

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
        vol.Optional("overwrite", default=True): cv.boolean,
    }
)


def _entry_config(entry: ConfigEntry) -> dict[str, Any]:
    config = dict(entry.data)
    config.update(entry.options)
    return config


def _should_overwrite_on_options_update(config_data: dict[str, Any]) -> bool:
    """Keep manual edits by default; overwrite only when bootstrap-only mode is disabled."""
    return not bool(config_data.get(CONF_BOOTSTRAP_ONLY, DEFAULT_BOOTSTRAP_ONLY))


async def _notify_generation(
    hass: HomeAssistant, *, title: str, dashboard_path: str, package_path: str
) -> None:
    persistent_notification.async_create(
        hass,
        (
            "SBB Dashboard Cards files generated.\n\n"
            f"- Dashboard: `{dashboard_path}`\n"
            f"- Package: `{package_path}`\n\n"
            "If packages are enabled, reload/restart Home Assistant after copying/using these files."
        ),
        title=title,
        notification_id=f"{DOMAIN}_generated",
    )


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration domain."""
    hass.data.setdefault(DOMAIN, {})

    async def _handle_generate_files(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        overwrite = call.data["overwrite"]

        if entry_id:
            entry = hass.config_entries.async_get_entry(entry_id)
            if not entry or entry.domain != DOMAIN:
                raise HomeAssistantError(f"Config entry not found for domain '{DOMAIN}': {entry_id}")
            entries = [entry]
        else:
            entries = hass.config_entries.async_entries(DOMAIN)

        if not entries:
            raise HomeAssistantError(f"No config entries found for domain '{DOMAIN}'.")

        for entry in entries:
            config_data = _entry_config(entry)
            try:
                generated = await async_generate_files(hass, config_data, overwrite=overwrite)
            except ValueError as err:
                raise HomeAssistantError(str(err)) from err
            await _notify_generation(
                hass,
                title="SBB Dashboard Cards",
                dashboard_path=generated["dashboard_path"],
                package_path=generated["package_path"],
            )

    if not hass.services.has_service(DOMAIN, SERVICE_GENERATE_FILES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GENERATE_FILES,
            _handle_generate_files,
            schema=SERVICE_SCHEMA,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    config_data = _entry_config(entry)
    try:
        generated = await async_generate_files(hass, config_data, overwrite=False)
    except ValueError as err:
        _LOGGER.error("Failed to generate initial files: %s", err)
        return False
    await _notify_generation(
        hass,
        title="SBB Dashboard Cards - Initial Files",
        dashboard_path=generated["dashboard_path"],
        package_path=generated["package_path"],
    )

    async def _update_listener(hass: HomeAssistant, updated_entry: ConfigEntry) -> None:
        updated_config = _entry_config(updated_entry)
        try:
            updated_paths = await async_generate_files(
                hass,
                updated_config,
                overwrite=_should_overwrite_on_options_update(updated_config),
            )
        except ValueError as err:
            _LOGGER.error("Failed to regenerate files from options update: %s", err)
            return
        await _notify_generation(
            hass,
            title="SBB Dashboard Cards - Files Updated",
            dashboard_path=updated_paths["dashboard_path"],
            package_path=updated_paths["package_path"],
        )

    entry.async_on_unload(entry.add_update_listener(_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
