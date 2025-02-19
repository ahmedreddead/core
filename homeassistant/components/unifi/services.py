"""UniFi services."""

import voluptuous as vol

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN as UNIFI_DOMAIN

SERVICE_RECONNECT_CLIENT = "reconnect_client"
SERVICE_REMOVE_CLIENTS = "remove_clients"

SERVICE_RECONNECT_CLIENT_SCHEMA = vol.All(
    vol.Schema({vol.Required(ATTR_DEVICE_ID): str})
)

SUPPORTED_SERVICES = (SERVICE_RECONNECT_CLIENT, SERVICE_REMOVE_CLIENTS)

SERVICE_TO_SCHEMA = {
    SERVICE_RECONNECT_CLIENT: SERVICE_RECONNECT_CLIENT_SCHEMA,
}


@callback
def async_setup_services(hass) -> None:
    """Set up services for UniFi integration."""

    services = {
        SERVICE_RECONNECT_CLIENT: async_reconnect_client,
        SERVICE_REMOVE_CLIENTS: async_remove_clients,
    }

    async def async_call_unifi_service(service_call) -> None:
        """Call correct UniFi service."""
        await services[service_call.service](hass, service_call.data)

    for service in SUPPORTED_SERVICES:
        hass.services.async_register(
            UNIFI_DOMAIN,
            service,
            async_call_unifi_service,
            schema=SERVICE_TO_SCHEMA.get(service),
        )


@callback
def async_unload_services(hass) -> None:
    """Unload UniFi services."""
    for service in SUPPORTED_SERVICES:
        hass.services.async_remove(UNIFI_DOMAIN, service)


async def async_reconnect_client(hass, data) -> None:
    """Try to get wireless client to reconnect to Wi-Fi."""
    device_registry = await hass.helpers.device_registry.async_get_registry()
    device_entry = device_registry.async_get(data[ATTR_DEVICE_ID])

    mac = ""
    for connection in device_entry.connections:
        if connection[0] == CONNECTION_NETWORK_MAC:
            mac = connection[1]
            break

    if mac == "":
        return

    for controller in hass.data[UNIFI_DOMAIN].values():
        if (
            not controller.available
            or (client := controller.api.clients[mac]) is None
            or client.is_wired
        ):
            continue

        await controller.api.clients.async_reconnect(mac)


async def async_remove_clients(hass, data) -> None:
    """Remove select clients from controller.

    Validates based on:
    - Total time between first seen and last seen is less than 15 minutes.
    - Neither IP, hostname nor name is configured.
    """
    for controller in hass.data[UNIFI_DOMAIN].values():

        if not controller.available:
            continue

        clients_to_remove = []

        for client in controller.api.clients_all.values():

            if client.last_seen - client.first_seen > 900:
                continue

            if any({client.fixed_ip, client.hostname, client.name}):
                continue

            clients_to_remove.append(client.mac)

        if clients_to_remove:
            await controller.api.clients.remove_clients(macs=clients_to_remove)
