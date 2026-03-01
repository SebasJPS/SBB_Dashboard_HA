"""Constants for the SBB Dashboard Cards integration."""

DOMAIN = "sbb_dashboard_cards"

CONF_LIGHT_MAIN = "light_main"
CONF_CAMERA_MAIN = "camera_main"
CONF_LIGHT_HALL = "light_hall"
CONF_SWITCH_PUMP = "switch_pump"
CONF_LOCK_DOOR = "lock_door"
CONF_EVENT_MOTION = "event_motion"
CONF_EVENT_DOORBELL = "event_doorbell"
CONF_EVENT_ALARM = "event_alarm"
CONF_INCLUDE_TEST_TRIGGERS = "include_test_triggers"
CONF_DASHBOARD_FILENAME = "dashboard_filename"
CONF_PACKAGE_FILENAME = "package_filename"

DEFAULT_DASHBOARD_FILENAME = "sbb_dashboard_cards_dashboard.yaml"
DEFAULT_PACKAGE_FILENAME = "packages/sbb_dashboard_cards.yaml"
DEFAULT_INCLUDE_TEST_TRIGGERS = True

SERVICE_GENERATE_FILES = "generate_files"
