"""The syncthru component."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
from pysyncthru import ConnectionMode, SyncThru, SyncThruAPINotSupported

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up config entry."""

    session = aiohttp_client.async_get_clientsession(hass)
    hass.data.setdefault(DOMAIN, {})
    printer = SyncThru(
        entry.data[CONF_URL], session, connection_mode=ConnectionMode.API
    )

    async def async_update_data() -> SyncThru:
        """Fetch data from the printer."""
        try:
            async with async_timeout.timeout(10):
                await printer.update()
        except SyncThruAPINotSupported as api_error:
            # if an exception is thrown, printer does not support syncthru
            _LOGGER.info(
                "Configured printer at %s does not provide SyncThru JSON API",
                printer.url,
                exc_info=api_error,
            )
            raise api_error
        else:
            # if the printer is offline, we raise an UpdateFailed
            if printer.is_unknown_state():
                raise UpdateFailed(
                    f"Configured printer at {printer.url} does not respond."
                )
            return printer

    coordinator: DataUpdateCoordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    if isinstance(coordinator.last_exception, SyncThruAPINotSupported):
        # this means that the printer does not support the syncthru JSON API
        # and the config should simply be discarded
        return False

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections=device_connections(printer),
        identifiers=device_identifiers(printer),
        model=printer.model(),
        name=printer.hostname(),
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


def device_identifiers(printer: SyncThru) -> set[tuple[str, str]] | None:
    """Get device identifiers for device registry."""
    serial = printer.serial_number()
    if serial is None:
        return None
    return {(DOMAIN, serial)}


def device_connections(printer: SyncThru) -> set[tuple[str, str]]:
    """Get device connections for device registry."""
    if mac := printer.raw().get("identity", {}).get("mac_addr"):
        return {(dr.CONNECTION_NETWORK_MAC, mac)}
    return set()
