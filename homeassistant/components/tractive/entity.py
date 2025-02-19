"""A entity class for Tractive integration."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class TractiveEntity(Entity):
    """Tractive entity class."""

    def __init__(
        self, user_id: str, trackable: dict[str, Any], tracker_details: dict[str, Any]
    ) -> None:
        """Initialize tracker entity."""
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, tracker_details["_id"])},
            name=f"Tractive ({tracker_details['_id']})",
            manufacturer="Tractive GmbH",
            sw_version=tracker_details["fw_version"],
            model=tracker_details["model_number"],
        )
        self._user_id = user_id
        self._tracker_id = tracker_details["_id"]
        self._trackable = trackable
