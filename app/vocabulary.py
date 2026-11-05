"""Known entities and actions of the Metis voice assistant.

Entities form a hierarchy: an area contains fixtures, a fixture may
have several bulbs. A command can target any level; resolve() maps it
to the devices that can actually be switched.

Field "z2m" is the friendly_name in Zigbee2MQTT. None means the level
exists here as a logical group but not yet in Zigbee2MQTT.
"""

ACTIONS: dict[str, list[str]] = {
    "turn_on": ["turn on", "switch on", "activate"],
    "turn_off": ["turn off", "switch off", "deactivate"],
    "set_brightness": ["set", "dim", "brightness"],
}

ENTITIES: dict[str, dict] = {
    # --- Areas ----------------------------------------------------
    "light.all": {
        "kind": "area",
        "z2m": None,
        "aliases": ["all the lights", "all lights", "everything"],
        "members": [
            "light.alexandria",
            "light.entrance",
            "light.living_room",
            "light.kitchen",
            "light.bedroom",
            "light.tolomeo",
        ],
    },
    "light.alexandria": {
        "kind": "area",
        "z2m": "Alexandria",
        "aliases": ["alexandria", "library", "bookshelf", "bookshelf lights"],
        "members": [
            "light.alexandria_lamp_1",
            "light.alexandria_lamp_2",
            "light.alexandria_lamp_3",
            "light.alexandria_lamp_4",
        ],
    },
    "light.entrance": {
        "kind": "area",
        "z2m": "entrance",
        "aliases": ["entrance", "entrance light", "hallway"],
        "members": [],
    },
    "light.living_room": {
        "kind": "area",
        "z2m": "living room",
        "aliases": ["living room", "living room lights"],
        "members": ["light.living_room_1"],
    },
    "light.kitchen": {
        "kind": "area",
        "z2m": "Kitchen",
        "aliases": ["kitchen", "kitchen lights"],
        "members": ["light.kitchen_1", "light.kitchen_2"],
    },
    "light.bedroom": {
        "kind": "area",
        "z2m": "bedroom",
        "aliases": ["bedroom", "bedroom lights"],
        "members": ["light.bedroom_1", "light.bed_1"],
    },

    # --- Bookshelf fixtures ---------------------------------------
    "light.alexandria_lamp_1": {
        "kind": "fixture",
        "z2m": None,
        "aliases": ["library 1", "alexandria 1", "bookshelf 1"],
        "members": ["light.alexandria_bulb_1", "light.alexandria_bulb_2"],
    },
    "light.alexandria_lamp_2": {
        "kind": "fixture",
        "z2m": None,
        "aliases": ["library 2", "alexandria 2", "bookshelf 2"],
        "members": ["light.alexandria_bulb_3", "light.alexandria_bulb_4"],
    },
    "light.alexandria_lamp_3": {
        "kind": "fixture",
        "z2m": None,
        "aliases": ["library 3", "alexandria 3", "bookshelf 3"],
        "members": ["light.alexandria_bulb_5", "light.alexandria_bulb_6"],
    },
    "light.alexandria_lamp_4": {
        "kind": "fixture",
        "z2m": None,
        "aliases": ["library 4", "alexandria 4", "bookshelf 4"],
        "members": ["light.alexandria_bulb_7"],
    },

    # --- Bookshelf bulbs ------------------------------------------
    "light.alexandria_bulb_1": {
        "kind": "bulb", "z2m": "Alexandria 1",
        "aliases": ["library 1a", "alexandria 1a"], "members": [],
    },
    "light.alexandria_bulb_2": {
        "kind": "bulb", "z2m": "Alexandria 2",
        "aliases": ["library 1b", "alexandria 1b"], "members": [],
    },
    "light.alexandria_bulb_3": {
        "kind": "bulb", "z2m": "Alexandria 3",
        "aliases": ["library 2a", "alexandria 2a"], "members": [],
    },
    "light.alexandria_bulb_4": {
        "kind": "bulb", "z2m": "Alexandria 4",
        "aliases": ["library 2b", "alexandria 2b"], "members": [],
    },
    "light.alexandria_bulb_5": {
        "kind": "bulb", "z2m": "Alexandria 5",
        "aliases": ["library 3a", "alexandria 3a"], "members": [],
    },
    "light.alexandria_bulb_6": {
        "kind": "bulb", "z2m": "Alexandria 6",
        "aliases": ["library 3b", "alexandria 3b"], "members": [],
    },
    "light.alexandria_bulb_7": {
        "kind": "bulb", "z2m": "Alexandria 7",
        "aliases": ["library 4a", "alexandria 4a"], "members": [],
    },

    # --- Individual fixtures per room -----------------------------
    "light.living_room_1": {
        "kind": "fixture", "z2m": "living room 1",
        "aliases": ["living room 1"], "members": [],
    },
    "light.kitchen_1": {
        "kind": "fixture", "z2m": "Kitchen 1",
        "aliases": ["kitchen 1"], "members": [],
    },
    "light.kitchen_2": {
        "kind": "fixture", "z2m": "kitchen 2",
        "aliases": ["kitchen 2"], "members": [],
    },
    "light.bedroom_1": {
        "kind": "fixture", "z2m": "bedroom 1",
        "aliases": ["bedroom 1"], "members": [],
    },
    "light.bed_1": {
        "kind": "fixture", "z2m": "bed 1",
        "aliases": ["bed 1", "bed light"], "members": [],
    },
    "light.tolomeo": {
        "kind": "fixture", "z2m": "Tolomeo",
        "aliases": ["tolomeo", "desk lamp", "desk light"], "members": [],
    },
}


def resolve(entity_id: str) -> list[str]:
    """Resolves an entity to the switchable devices below it.

    If the entity has a Zigbee2MQTT name of its own it is switched
    directly (group multicast). Otherwise the members are traversed
    recursively.
    """
    entry = ENTITIES[entity_id]
    if entry["z2m"] is not None:
        return [entity_id]
    out: list[str] = []
    for member in entry["members"]:
        out.extend(resolve(member))
    return out


def all_entity_aliases() -> list[tuple[str, str]]:
    """All (alias, entity id) pairs as a flat list."""
    return [
        (alias, entity_id)
        for entity_id, entry in ENTITIES.items()
        for alias in entry["aliases"]
    ]


def all_action_aliases() -> list[tuple[str, str]]:
    """All (alias, action id) pairs as a flat list."""
    return [
        (alias, action)
        for action, aliases in ACTIONS.items()
        for alias in aliases
    ]
