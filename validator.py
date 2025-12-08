## sample validator from chat gpt. Haven't started gutting it yet. Migraine killing me so it might be a few days.

class ItemDefinitionError(Exception):
    pass


class ItemDefinitionValidator:
    """
    Validates all item definitions to ensure they follow required schema,
    have correct datatypes, and reference only valid items/types.
    """

    def __init__(self, definitions: dict):
        self.defs = definitions
        self.errors = []
        self.valid_types = {"misc", "container", "weapon", "food", "flower"}  # customize as needed

    def validate_all(self):
        for item_id, data in self.defs.items():
            self.validate_item(item_id, data)

        if self.errors:
            msg = "\n".join(self.errors)
            raise ItemDefinitionError(f"Item definition validation failed:\n{msg}")

    # ---------------------------
    # Validation Helpers
    # ---------------------------

    def validate_item(self, item_id: str, data: dict):
        self._require_fields(item_id, data)
        self._validate_basic_types(item_id, data)
        self._validate_container_rules(item_id, data)
        self._validate_children_rules(item_id, data)

    def _require_fields(self, item_id, data):
        required = ["name", "description", "type"]
        for field in required:
            if field not in data:
                self.errors.append(f"{item_id}: Missing required field '{field}'.")

    def _validate_basic_types(self, item_id, data):
        if "type" in data and not isinstance(data["type"], str):
            self.errors.append(f"{item_id}: field 'type' must be a string.")

        if "type" in data and data["type"] not in self.valid_types:
            self.errors.append(
                f"{item_id}: unknown type '{data['type']}'. "
                f"Valid types: {sorted(self.valid_types)}"
            )

        if "children" in data and not isinstance(data["children"], list):
            self.errors.append(f"{item_id}: 'children' must be a list.")

    def _validate_container_rules(self, item_id, data):
        if data.get("type") == "container":
            # container block required
            container = data.get("container")
            if not isinstance(container, dict):
                self.errors.append(f"{item_id}: container type must include a 'container' dict.")
                return

            if "capacity" not in container or not isinstance(container["capacity"], int):
                self.errors.append(f"{item_id}: container must define integer 'capacity'.")

            if "accepts" not in container or not isinstance(container["accepts"], list):
                self.errors.append(f"{item_id}: container must define list 'accepts'.")

        else:
            # Non-container items must NOT have container-specific keys
            if "container" in data:
                self.errors.append(
                    f"{item_id}: non-container item should not define a 'container' block."
                )

    def _validate_children_rules(self, item_id, data):
        if "children" in data:
            for child_id in data["children"]:
                if child_id not in self.defs:
                    self.errors.append(f"{item_id}: child '{child_id}' does not exist in definitions.")

                # Prevent circular parent references (simple version)
                if item_id in self.defs.get(child_id, {}).get("children", []):
                    self.errors.append(f"{item_id}: circular child relationship with '{child_id}'.")
