"""Nexia constants."""

PLATFORMS = ["sensor", "binary_sensor", "climate", "scene"]

ATTRIBUTION = "Data provided by mynexia.com"

NOTIFICATION_ID = "nexia_notification"
NOTIFICATION_TITLE = "Nexia Setup"

CONF_BRAND = "brand"

NEXIA_SCAN_INTERVAL = "scan_interval"

DOMAIN = "nexia"
DEFAULT_ENTITY_NAMESPACE = "nexia"

ATTR_DESCRIPTION = "description"

ATTR_AIRCLEANER_MODE = "aircleaner_mode"

ATTR_ZONE_STATUS = "zone_status"
ATTR_HUMIDIFY_SUPPORTED = "humidify_supported"
ATTR_DEHUMIDIFY_SUPPORTED = "dehumidify_supported"
ATTR_HUMIDIFY_SETPOINT = "humidify_setpoint"
ATTR_DEHUMIDIFY_SETPOINT = "dehumidify_setpoint"


MANUFACTURER = "Trane"

SIGNAL_ZONE_UPDATE = "NEXIA_CLIMATE_ZONE_UPDATE"
SIGNAL_THERMOSTAT_UPDATE = "NEXIA_CLIMATE_THERMOSTAT_UPDATE"

BRAND_NEXIA_NAME = "Nexia"
BRAND_ASAIR_NAME = "American Standard Home"
BRAND_TRANE_NAME = "Trane Home"
