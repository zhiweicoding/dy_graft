from pydantic import BaseModel
from typing import Any, Optional


class BaseResponse(BaseModel):
    code: int
    message: Optional[str] = None
    data: Any = None

    def json(self, **kwargs):
        return {"code": self.code, "message": self.message, "data": self.data}
