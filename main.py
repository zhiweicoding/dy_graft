from fastapi import FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse
import os
import tempfile

app = FastAPI()


def remove_file(path: str):
    try:
        os.unlink(path)
    except Exception as e:
        print(f"Failed to delete temporary file {path}: {str(e)}")


@app.post("/receice_data/getPicPath")
async def get_image(background_tasks: BackgroundTasks, id: str = Form(...)):
    # 使用tempfile安全地创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(id)[1])
