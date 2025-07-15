import json
from typing import Any
from datetime import datetime
from fastapi.responses import JSONResponse

class SafeJSONResponse(JSONResponse):
    """JSON response class with datetime serialization safety."""
    
    def render(self, content: Any) -> bytes:
        """Override render method to handle datetime objects."""
        try:
            return super().render(content)
        except TypeError:
            return json.dumps(
                content,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
                default=self._handle_datetime_serialization
            ).encode("utf-8")
    
    def _handle_datetime_serialization(self, obj):
        """Custom handler for datetime serialization."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        else:
            return str(obj)
