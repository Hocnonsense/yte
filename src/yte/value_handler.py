from typing import Any
from sys import modules


def _scalar(value):
    return value


def _detect_numpy_import():
    if "numpy" in modules:
        import numpy as np  # type: ignore

        def numpy_scalar(value):
            if isinstance(value, np.ndarray):
                return value.tolist()
            if isinstance(value, np.generic):
                return value.item()
            return value

        def blank():
            pass

        global scalar, detect_numpy_import
        scalar = numpy_scalar
        detect_numpy_import = blank


scalar = _scalar
detect_numpy_import = _detect_numpy_import


class ValueHandler:

    def postprocess(self, value: Any) -> Any:
        detect_numpy_import()
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
        value = scalar(value)
        if isinstance(value, (list, dict)):
            return self._postprocess(value)
        return value
