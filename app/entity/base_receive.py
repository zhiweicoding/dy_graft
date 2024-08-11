from pydantic import BaseModel


class UploadReceive(BaseModel):
    download_url: str
    suffix: str
    cell_id: str
