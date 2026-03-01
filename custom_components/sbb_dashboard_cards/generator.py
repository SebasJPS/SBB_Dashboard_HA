"""File generation for SBB Dashboard Cards."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from homeassistant.core import HomeAssistant

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
    DEFAULT_PACKAGE_FILENAME,
)


def _event_entity(config: dict[str, Any], key: str, fallback: str) -> str:
    value = config.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _input_booleans(include_test_triggers: bool) -> dict[str, dict[str, str]]:
    booleans: dict[str, dict[str, str]] = {
        "light_wohnzimmer_color_mode": {
            "name": "Wohnzimmer Licht Farbmodus",
            "icon": "mdi:palette",
        },
        "camera_fullscreen_mode": {
            "name": "Kamera Vollbild Modus",
            "icon": "mdi:fit-to-screen",
        },
        "camera_auto_open_enabled": {
            "name": "Kamera Auto-Vollbild aktiv",
            "icon": "mdi:auto-mode",
        },
    }
    if include_test_triggers:
        booleans.update(
            {
                "camera_event_motion": {
                    "name": "Kamera Event Bewegung (Test)",
                    "icon": "mdi:motion-sensor",
                },
                "camera_event_doorbell": {
                    "name": "Kamera Event Klingel (Test)",
                    "icon": "mdi:doorbell-video",
                },
                "camera_event_alarm": {
                    "name": "Kamera Event Alarm (Test)",
                    "icon": "mdi:alarm-light",
                },
            }
        )
    return booleans


def _build_package_data(config: dict[str, Any]) -> dict[str, Any]:
    include_test = bool(config.get(CONF_INCLUDE_TEST_TRIGGERS, True))
    event_motion = _event_entity(
        config, CONF_EVENT_MOTION, "input_boolean.camera_event_motion"
    )
    event_doorbell = _event_entity(
        config, CONF_EVENT_DOORBELL, "input_boolean.camera_event_doorbell"
    )
    event_alarm = _event_entity(config, CONF_EVENT_ALARM, "input_boolean.camera_event_alarm")

    condition_state = (
        "{{\n"
        f"  is_state('{event_motion}', 'on')\n"
        f"  or is_state('{event_doorbell}', 'on')\n"
        f"  or is_state('{event_alarm}', 'on')\n"
        "}}"
    )

    return {
        "input_boolean": _input_booleans(include_test),
        "timer": {
            "light_wohnzimmer_color_mode_window": {
                "name": "Licht Farbmodus Fenster",
                "duration": "00:00:12",
            },
            "camera_fullscreen_window": {
                "name": "Kamera Vollbild Fenster",
                "duration": "00:01:30",
            },
        },
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": "Kamera Auto-Vollbild Bedingung",
                        "unique_id": "kamera_auto_vollbild_bedingung",
                        "state": condition_state,
                    }
                ]
            }
        ],
        "script": {
            "light_wohnzimmer_color_mode_enable": {
                "alias": "Dashboard - Licht Farbmodus starten",
                "mode": "restart",
                "sequence": [
                    {
                        "action": "input_boolean.turn_on",
                        "target": {"entity_id": "input_boolean.light_wohnzimmer_color_mode"},
                    },
                    {
                        "action": "timer.start",
                        "target": {"entity_id": "timer.light_wohnzimmer_color_mode_window"},
                        "data": {"duration": "00:00:12"},
                    },
                ],
            },
            "light_wohnzimmer_color_mode_disable": {
                "alias": "Dashboard - Licht Farbmodus beenden",
                "mode": "restart",
                "sequence": [
                    {
                        "action": "timer.cancel",
                        "target": {"entity_id": "timer.light_wohnzimmer_color_mode_window"},
                    },
                    {
                        "action": "input_boolean.turn_off",
                        "target": {"entity_id": "input_boolean.light_wohnzimmer_color_mode"},
                    },
                ],
            },
            "camera_open_fullscreen": {
                "alias": "Dashboard - Kamera Vollbild an",
                "mode": "restart",
                "sequence": [
                    {
                        "action": "input_boolean.turn_on",
                        "target": {"entity_id": "input_boolean.camera_fullscreen_mode"},
                    },
                    {
                        "action": "timer.start",
                        "target": {"entity_id": "timer.camera_fullscreen_window"},
                        "data": {"duration": "00:01:30"},
                    },
                ],
            },
            "camera_close_fullscreen": {
                "alias": "Dashboard - Kamera Vollbild aus",
                "mode": "restart",
                "sequence": [
                    {
                        "action": "timer.cancel",
                        "target": {"entity_id": "timer.camera_fullscreen_window"},
                    },
                    {
                        "action": "input_boolean.turn_off",
                        "target": {"entity_id": "input_boolean.camera_fullscreen_mode"},
                    },
                ],
            },
        },
        "automation": [
            {
                "id": "dashboard_light_color_mode_timeout",
                "alias": "Dashboard - Licht Farbmodus Timeout",
                "trigger": [
                    {
                        "platform": "event",
                        "event_type": "timer.finished",
                        "event_data": {
                            "entity_id": "timer.light_wohnzimmer_color_mode_window"
                        },
                    }
                ],
                "action": [
                    {
                        "action": "input_boolean.turn_off",
                        "target": {"entity_id": "input_boolean.light_wohnzimmer_color_mode"},
                    }
                ],
            },
            {
                "id": "dashboard_camera_auto_open",
                "alias": "Dashboard - Kamera bei Event in Vollbild",
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "binary_sensor.kamera_auto_vollbild_bedingung",
                        "from": "off",
                        "to": "on",
                    }
                ],
                "condition": [
                    {
                        "condition": "state",
                        "entity_id": "input_boolean.camera_auto_open_enabled",
                        "state": "on",
                    }
                ],
                "action": [{"action": "script.camera_open_fullscreen"}],
            },
            {
                "id": "dashboard_camera_extend_timeout_on_event",
                "alias": "Dashboard - Kamera Vollbild Timeout verlaengern bei Event",
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "binary_sensor.kamera_auto_vollbild_bedingung",
                        "to": "on",
                    }
                ],
                "condition": [
                    {
                        "condition": "state",
                        "entity_id": "input_boolean.camera_fullscreen_mode",
                        "state": "on",
                    }
                ],
                "action": [
                    {
                        "action": "timer.start",
                        "target": {"entity_id": "timer.camera_fullscreen_window"},
                        "data": {"duration": "00:01:30"},
                    }
                ],
            },
            {
                "id": "dashboard_camera_fullscreen_timeout",
                "alias": "Dashboard - Kamera Vollbild Timeout",
                "trigger": [
                    {
                        "platform": "event",
                        "event_type": "timer.finished",
                        "event_data": {"entity_id": "timer.camera_fullscreen_window"},
                    }
                ],
                "condition": [
                    {
                        "condition": "state",
                        "entity_id": "binary_sensor.kamera_auto_vollbild_bedingung",
                        "state": "off",
                    }
                ],
                "action": [
                    {
                        "action": "input_boolean.turn_off",
                        "target": {"entity_id": "input_boolean.camera_fullscreen_mode"},
                    }
                ],
            },
        ],
    }


def _build_test_trigger_grid() -> dict[str, Any]:
    return {
        "type": "grid",
        "title": "Test Trigger (fuer V2 Mockup)",
        "columns": 3,
        "square": False,
        "cards": [
            {
                "type": "button",
                "entity": "input_boolean.camera_event_motion",
                "name": "Bewegung",
                "icon": "mdi:motion-sensor",
                "tap_action": {"action": "toggle"},
            },
            {
                "type": "button",
                "entity": "input_boolean.camera_event_doorbell",
                "name": "Klingel",
                "icon": "mdi:doorbell-video",
                "tap_action": {"action": "toggle"},
            },
            {
                "type": "button",
                "entity": "input_boolean.camera_event_alarm",
                "name": "Alarm",
                "icon": "mdi:alarm-light",
                "tap_action": {"action": "toggle"},
            },
        ],
    }


def _replace_entities(obj: Any, replacements: dict[str, str]) -> Any:
    if isinstance(obj, dict):
        return {key: _replace_entities(value, replacements) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_replace_entities(value, replacements) for value in obj]
    if isinstance(obj, str):
        return replacements.get(obj, obj)
    return obj


def _base_dashboard_data() -> dict[str, Any]:
    return {
        "title": "Dashboard Cards Mockup",
        "views": [
            {
                "title": "Wohnzimmer",
                "path": "wohnzimmer",
                "icon": "mdi:sofa",
                "cards": [
                    {
                        "type": "vertical-stack",
                        "cards": [
                            {
                                "type": "markdown",
                                "content": (
                                    "## Licht Card v2\n"
                                    "- Tap: An/Aus\n"
                                    "- Slider: Dimmen (Normalmodus)\n"
                                    "- Double-Tap: Farbmodus fuer 12 Sekunden\n"
                                ),
                            },
                            {
                                "type": "conditional",
                                "conditions": [
                                    {
                                        "entity": "input_boolean.light_wohnzimmer_color_mode",
                                        "state": "off",
                                    }
                                ],
                                "card": {
                                    "type": "tile",
                                    "entity": "__LIGHT_MAIN__",
                                    "name": "Wohnzimmer Licht",
                                    "icon": "mdi:lightbulb",
                                    "tap_action": {"action": "toggle"},
                                    "hold_action": {"action": "more-info"},
                                    "double_tap_action": {
                                        "action": "perform-action",
                                        "perform_action": "script.light_wohnzimmer_color_mode_enable",
                                    },
                                    "features": [{"type": "light-brightness"}],
                                    "state_content": ["state", "brightness"],
                                },
                            },
                            {
                                "type": "conditional",
                                "conditions": [
                                    {
                                        "entity": "input_boolean.light_wohnzimmer_color_mode",
                                        "state": "on",
                                    }
                                ],
                                "card": {
                                    "type": "tile",
                                    "entity": "__LIGHT_MAIN__",
                                    "name": "Wohnzimmer Farbe",
                                    "icon": "mdi:palette",
                                    "color": "accent",
                                    "tap_action": {"action": "toggle"},
                                    "hold_action": {"action": "more-info"},
                                    "double_tap_action": {
                                        "action": "perform-action",
                                        "perform_action": "script.light_wohnzimmer_color_mode_disable",
                                    },
                                    "features": [{"type": "light-color"}],
                                    "state_content": ["state"],
                                },
                            },
                            {
                                "type": "conditional",
                                "conditions": [
                                    {
                                        "entity": "input_boolean.light_wohnzimmer_color_mode",
                                        "state": "on",
                                    }
                                ],
                                "card": {
                                    "type": "tile",
                                    "entity": "timer.light_wohnzimmer_color_mode_window",
                                    "name": "Farbmodus Restzeit",
                                    "icon": "mdi:timer-sand",
                                    "state_content": ["state"],
                                },
                            },
                        ],
                    },
                    {
                        "type": "vertical-stack",
                        "cards": [
                            {
                                "type": "markdown",
                                "content": (
                                    "## Video Card v2 (nativ, ohne browser_mod)\n"
                                    "- Tap: Grossansicht im Dashboard\n"
                                    "- Auto-Grossansicht bei Events (Bewegung/Klingel/Alarm)\n"
                                    "- Auto-Timeout schliesst die Grossansicht wieder\n"
                                ),
                            },
                            {
                                "type": "conditional",
                                "conditions": [
                                    {
                                        "entity": "input_boolean.camera_fullscreen_mode",
                                        "state": "off",
                                    }
                                ],
                                "card": {
                                    "type": "vertical-stack",
                                    "cards": [
                                        {
                                            "type": "picture-entity",
                                            "entity": "__CAMERA_MAIN__",
                                            "name": "Haustuer Kamera (Normal)",
                                            "show_state": False,
                                            "camera_view": "live",
                                            "tap_action": {
                                                "action": "perform-action",
                                                "perform_action": "script.camera_open_fullscreen",
                                            },
                                        },
                                        {
                                            "type": "grid",
                                            "title": "Schnelle Aktionen",
                                            "columns": 2,
                                            "square": False,
                                            "cards": [
                                                {
                                                    "type": "button",
                                                    "entity": "__LIGHT_HALL__",
                                                    "name": "Flur",
                                                    "icon": "mdi:lightbulb",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "__SWITCH_PUMP__",
                                                    "name": "Pumpe",
                                                    "icon": "mdi:water-pump",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "__LOCK_DOOR__",
                                                    "name": "Tuer",
                                                    "icon": "mdi:lock",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "input_boolean.camera_fullscreen_mode",
                                                    "name": "Grossansicht",
                                                    "icon": "mdi:fit-to-screen",
                                                    "tap_action": {
                                                        "action": "perform-action",
                                                        "perform_action": "script.camera_open_fullscreen",
                                                    },
                                                },
                                            ],
                                        },
                                        {
                                            "type": "entities",
                                            "title": "Auto-Vollbild",
                                            "entities": [
                                                {
                                                    "entity": "input_boolean.camera_auto_open_enabled",
                                                    "name": "Auto-Modus aktiv",
                                                },
                                                {
                                                    "entity": "binary_sensor.kamera_auto_vollbild_bedingung",
                                                    "name": "Bedingung aktuell",
                                                },
                                                {
                                                    "entity": "timer.camera_fullscreen_window",
                                                    "name": "Vollbild Timeout",
                                                },
                                            ],
                                        },
                                    ],
                                },
                            },
                            {
                                "type": "conditional",
                                "conditions": [
                                    {
                                        "entity": "input_boolean.camera_fullscreen_mode",
                                        "state": "on",
                                    }
                                ],
                                "card": {
                                    "type": "vertical-stack",
                                    "cards": [
                                        {
                                            "type": "markdown",
                                            "content": (
                                                "### Kamera Grossansicht\n"
                                                'Tap aufs Bild oder auf "Schliessen", um zurueckzugehen.\n'
                                            ),
                                        },
                                        {
                                            "type": "picture-entity",
                                            "entity": "__CAMERA_MAIN__",
                                            "name": "Haustuer Kamera (Gross)",
                                            "show_state": False,
                                            "camera_view": "live",
                                            "tap_action": {
                                                "action": "perform-action",
                                                "perform_action": "script.camera_close_fullscreen",
                                            },
                                        },
                                        {
                                            "type": "grid",
                                            "title": "Steuerung unter Video",
                                            "columns": 2,
                                            "square": False,
                                            "cards": [
                                                {
                                                    "type": "button",
                                                    "entity": "__LIGHT_HALL__",
                                                    "name": "Flur",
                                                    "icon": "mdi:lightbulb",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "__LOCK_DOOR__",
                                                    "name": "Tuer",
                                                    "icon": "mdi:lock",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "__SWITCH_PUMP__",
                                                    "name": "Pumpe",
                                                    "icon": "mdi:water-pump",
                                                    "tap_action": {"action": "toggle"},
                                                },
                                                {
                                                    "type": "button",
                                                    "entity": "input_boolean.camera_fullscreen_mode",
                                                    "name": "Schliessen",
                                                    "icon": "mdi:close",
                                                    "tap_action": {
                                                        "action": "perform-action",
                                                        "perform_action": "script.camera_close_fullscreen",
                                                    },
                                                },
                                            ],
                                        },
                                        {
                                            "type": "entities",
                                            "title": "Vollbild Status",
                                            "entities": [
                                                {
                                                    "entity": "timer.camera_fullscreen_window",
                                                    "name": "Restzeit",
                                                },
                                                {
                                                    "entity": "binary_sensor.kamera_auto_vollbild_bedingung",
                                                    "name": "Event noch aktiv",
                                                },
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            }
        ],
    }


def _build_dashboard_data(config: dict[str, Any]) -> dict[str, Any]:
    dashboard = deepcopy(_base_dashboard_data())
    replacements = {
        "__LIGHT_MAIN__": config[CONF_LIGHT_MAIN],
        "__CAMERA_MAIN__": config[CONF_CAMERA_MAIN],
        "__LIGHT_HALL__": config[CONF_LIGHT_HALL],
        "__SWITCH_PUMP__": config[CONF_SWITCH_PUMP],
        "__LOCK_DOOR__": config[CONF_LOCK_DOOR],
    }
    dashboard = _replace_entities(dashboard, replacements)
    if bool(config.get(CONF_INCLUDE_TEST_TRIGGERS, True)):
        video_stack_cards = dashboard["views"][0]["cards"][1]["cards"]
        video_stack_cards.append(_build_test_trigger_grid())
    return dashboard


def _safe_join_in_config_dir(hass: HomeAssistant, user_path: str) -> Path:
    config_root = Path(hass.config.path("")).resolve()
    candidate = Path(user_path)
    if not candidate.is_absolute():
        candidate = config_root / candidate
    candidate = candidate.resolve()
    if config_root != candidate and config_root not in candidate.parents:
        raise ValueError(f"Path must be inside Home Assistant config directory: {user_path}")
    return candidate


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


async def async_generate_files(
    hass: HomeAssistant, config: dict[str, Any], *, overwrite: bool
) -> dict[str, str]:
    dashboard_path = _safe_join_in_config_dir(
        hass, str(config.get(CONF_DASHBOARD_FILENAME, DEFAULT_DASHBOARD_FILENAME))
    )
    package_path = _safe_join_in_config_dir(
        hass, str(config.get(CONF_PACKAGE_FILENAME, DEFAULT_PACKAGE_FILENAME))
    )

    dashboard_yaml = _dump_yaml(_build_dashboard_data(config))
    package_yaml = _dump_yaml(_build_package_data(config))

    def _write_file(path: Path, content: str) -> None:
        if path.exists() and not overwrite:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    await hass.async_add_executor_job(_write_file, dashboard_path, dashboard_yaml)
    await hass.async_add_executor_job(_write_file, package_path, package_yaml)

    return {
        "dashboard_path": str(dashboard_path),
        "package_path": str(package_path),
    }
