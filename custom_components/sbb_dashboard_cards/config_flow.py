"""Config flow for SBB Dashboard Cards."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CAMERA_MAIN,
    CONF_DASHBOARD_FILENAME,
    CONF_EVENT_ALARM,
    CONF_EVENT_DOORBELL,
    CONF_EVENT_MOTION,
    CONF_INCLUDE_TEST_TRIGGERS,
    CONF_LIGHT_HALL,
    CONF_LIGHT_MAIN,
    CONF_LOCK_DOOR,
    CONF_PACKAGE_FILENAME,
    CONF_SWITCH_PUMP,
    DEFAULT_DASHBOARD_FILENAME,
    DEFAULT_INCLUDE_TEST_TRIGGERS,
    DEFAULT_PACKAGE_FILENAME,
    DOMAIN,
)


def _merged_entry_config(entry: config_entries.ConfigEntry) -> dict[str, Any]:
    values = dict(entry.data)
    values.update(entry.options)
    return values


def _validate_input(user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not str(user_input[CONF_DASHBOARD_FILENAME]).endswith(".yaml"):
        errors[CONF_DASHBOARD_FILENAME] = "yaml_required"
    if not str(user_input[CONF_PACKAGE_FILENAME]).endswith(".yaml"):
        errors[CONF_PACKAGE_FILENAME] = "yaml_required"

    if not user_input.get(CONF_INCLUDE_TEST_TRIGGERS):
        missing = [
            key
            for key in (CONF_EVENT_MOTION, CONF_EVENT_DOORBELL, CONF_EVENT_ALARM)
            if not user_input.get(key)
        ]
        if missing:
            errors["base"] = "event_entities_required"

    return errors


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    any_entity = selector.EntitySelector(selector.EntitySelectorConfig())
    text_selector = selector.TextSelector(selector.TextSelectorConfig())

    schema_map: dict[Any, Any] = {
        vol.Required(
            CONF_LIGHT_MAIN, default=defaults.get(CONF_LIGHT_MAIN, "light.wohnzimmer")
        ): any_entity,
        vol.Required(
            CONF_CAMERA_MAIN, default=defaults.get(CONF_CAMERA_MAIN, "camera.haustuer")
        ): any_entity,
        vol.Required(
            CONF_LIGHT_HALL, default=defaults.get(CONF_LIGHT_HALL, "light.flur")
        ): any_entity,
        vol.Required(
            CONF_SWITCH_PUMP, default=defaults.get(CONF_SWITCH_PUMP, "switch.gartenpumpe")
        ): any_entity,
        vol.Required(
            CONF_LOCK_DOOR, default=defaults.get(CONF_LOCK_DOOR, "lock.haustuer")
        ): any_entity,
    }

    for key in (CONF_EVENT_MOTION, CONF_EVENT_DOORBELL, CONF_EVENT_ALARM):
        if defaults.get(key):
            schema_map[vol.Optional(key, default=defaults[key])] = any_entity
        else:
            schema_map[vol.Optional(key)] = any_entity

    schema_map[
        vol.Required(
            CONF_INCLUDE_TEST_TRIGGERS,
            default=defaults.get(CONF_INCLUDE_TEST_TRIGGERS, DEFAULT_INCLUDE_TEST_TRIGGERS),
        )
    ] = selector.BooleanSelector()
    schema_map[
        vol.Required(
            CONF_DASHBOARD_FILENAME,
            default=defaults.get(CONF_DASHBOARD_FILENAME, DEFAULT_DASHBOARD_FILENAME),
        )
    ] = text_selector
    schema_map[
        vol.Required(
            CONF_PACKAGE_FILENAME,
            default=defaults.get(CONF_PACKAGE_FILENAME, DEFAULT_PACKAGE_FILENAME),
        )
    ] = text_selector
    return vol.Schema(schema_map)


class DashboardCardsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SBB Dashboard Cards."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title="SBB Dashboard Cards",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema({}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return DashboardCardsOptionsFlow(config_entry)


class DashboardCardsOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for SBB Dashboard Cards."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        defaults = _merged_entry_config(self._config_entry)
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(defaults),
            errors=errors,
        )
