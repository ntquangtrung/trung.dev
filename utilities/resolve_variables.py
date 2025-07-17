import re
from typing import Any, Dict, Optional


class VariableResolver:

    def __init__(self, input_string: str, lookup_dict: Dict[str, Any]):
        if not isinstance(input_string, str) or not input_string.strip():
            raise ValueError("Input string must be a non-empty string.")
        if not isinstance(lookup_dict, dict):
            raise ValueError("Lookup dictionary must be a valid dictionary.")

        self.input_string = input_string
        self.lookup_dict = lookup_dict

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(r"\{variable\.([A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)*)\}")

    def resolve(self) -> str:
        return self.pattern.sub(self._replacer, self.input_string)

    def _replacer(self, match: re.Match) -> str:
        path = match.group(1)
        keys = path.split(".")
        value = self._get_nested_value(self.lookup_dict, keys)
        return str(value) if value is not None else match.group(0)

    def _get_nested_value(self, current: Any, keys: list[str]) -> Optional[Any]:
        for key in keys:
            lower_key = key.lower()
            if not isinstance(current, dict) or lower_key not in current:
                return None
            current = current[lower_key]
        return current
