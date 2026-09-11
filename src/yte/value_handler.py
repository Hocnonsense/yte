from typing import Any
from sys import modules


class HandleValue:
    @staticmethod
    def scalar(value):
        return value


_detected = False
_handle_value = HandleValue()


class ValueHandler:

    @classmethod
    def detect_numpy_import(cls):
        global _detected

        if _detected:
            return
        if "numpy" in modules:
            import numpy as np  # type: ignore

            class HandleNumpyValue(HandleValue):
                @staticmethod
                def scalar(value):
                    if isinstance(value, np.ndarray):
                        return value.tolist()
                    if isinstance(value, np.generic):
                        return value.item()
                    return value

            global _handle_value
            _handle_value = HandleNumpyValue()
            _detected = True

    def postprocess(self, value: Any) -> Any:
        self.detect_numpy_import()
        return self._postprocess(value)

    def _postprocess(self, value: Any) -> Any:
        if isinstance(value, list):
            return list(map(self._postprocess, value))
        elif isinstance(value, dict):
            return {
                self._postprocess(key): self._postprocess(value)
                for key, value in value.items()
            }
        else:
            return self.postprocess_atomic_value(value)

    def postprocess_atomic_value(self, value: Any) -> Any:
        return self._postprocess(_handle_value.scalar(value))
