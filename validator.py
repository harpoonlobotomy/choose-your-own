## 8/12/25 Base from gpt, starting to chop it up.

class ItemDefinitionError(Exception):
    pass


class ItemDefinitionValidator:
    """
    Validates item definitions and provides helpful auto-generated error hints.
    """

    def __init__(self, definitions: dict):
        self.defs = definitions
        self.errors = []
        self.valid_types = {"starting_location", "loot_type"}
        # You can expand this with your own game logic.

    # -----------------------------------
    # Core API
    # -----------------------------------

    def validate_all(self):
        for item_id, data in self.defs.items():
            self.validate_item(item_id, data)

        if self.errors:
            msg = "\n\n".join(self.errors)
            raise ItemDefinitionError(f"Item definition validation failed:\n\n{msg}")

    # -----------------------------------
    # Error formatting with hints
    # -----------------------------------

    def _error(self, item_id: str, message: str, hint: str | None = None):
        if hint:
            full_msg = f"{item_id}: {message}\n  Hint: {hint}"
        else:
            full_msg = f"{item_id}: {message}"
        self.errors.append(full_msg)

    # -----------------------------------
    # Validation logic
    # -----------------------------------

    def validate_item(self, item_id: str, data: dict):
        self._require_fields(item_id, data)
        self._validate_types(item_id, data)
        self._validate_container_rules(item_id, data)
        self._validate_child_rules(item_id, data)

    def _require_fields(self, item_id, data):
        required = ["name", "description", "flags"]

        for field in required:
            if field not in data:
                self._error(
                    item_id,
                    f"Missing required field '{field}'.",
                    hint=f"Add \"{field}\": <value> to this item."
                )

    def _validate_types(self, item_id, data):

        if not any(map(lambda v: v in self.valid_types, data)): ## not sure if this'll work, not tested.
            self._error(
                item_id,
                "Item must include either a start_location (for loc_loot) or a loot_type.",
                hint=f"Add either a starting_location: (location, cardinal) or a loot_type (minor_loot)."
            )


        for type in self.valid_types:

            t = data.get(type)

            if t and not isinstance(t, str):
                self._error(
                    item_id,
                    "'type' must be a string.",
                    hint="Use a text label like \"container\" or \"misc\"."
                )

            if t and t not in self.valid_types:
                self._error(
                    item_id,
                    f"Unknown type '{t}'.",
                    hint=f"Choose one of: {sorted(self.valid_types)}"
                )


    # -----------------------------------
    # Container logic
    # -----------------------------------

    def _validate_container_rules(self, item_id, data):
        t = data["flags"].get("container")

        if t:
            container_limits = data.get("container_limits")

            if not isinstance(container_limits, str):
                self._error(
                    item_id,
                    "Container items must include a 'container limits' entry.",
                    hint='Add: "container_limits": SMALLER_THAN_APPLE or other relevant size category.'
                )
                return


    # -----------------------------------
    # Children / Parent rules
    # -----------------------------------

    def _validate_child_rules(self, item_id, data):
        children = data.get("starting_children")

        if children:
            if not isinstance(children, list):
                self._error(
                    item_id,
                    "'children' must be a list of items.",
                    hint='Example: "children": ["dried_flowers"]'
                )
                return

            for child_id in children:
                if child_id not in self.defs:
                    self._error(
                        item_id,
                        f"Child '{child_id}' not found in definitions.",
                        hint=f"Make sure '{child_id}' is defined or remove it from this item."
                    )

                # Detect circular links
                child_data = self.defs.get(child_id, {})
                if item_id in child_data.get("children", []):
                    self._error(
                        item_id,
                        f"Circular child link with '{child_id}'.",
                        hint="Child items cannot list their parent as a child."
                    )
