from pathlib import Path
import uuid
import tempfile
import os
import json

from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.model import PostDetail
from f2.apps.douyin.utils import (
    AwemeIdFetcher,
)
from f2.i18n.translator import _
from f2.log.logger import logger
from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks

from app.db.postgres_db import RecordAction, RecordActionSchema
from app.entity.base_response import BaseResponse
from app.entity.filter_model import PostDetailFilter

from app.storage import storage_factory
from datetime import datetime
from app.dependencies import get_db
from sqlalchemy.orm import Session

router = APIRouter()

cdn_url = os.environ['CDN_URL']


@router.post("/query/finish/{record_id}", response_model=BaseResponse)
async def query_finish(record_id: str = Path(title="The ID of the record to get"),
                       db: Session = Depends(get_db)):
    one_data: type[RecordAction] = (db.query(RecordAction)
                                    .filter(RecordAction.record_id == record_id, RecordAction.is_finish == True)
                                    .first())
    if one_data is None:
        # raise HTTPException(status_code=404, detail="data not found")
        return BaseResponse(code=201, message="success", data={}).json()
    else:
        return BaseResponse(code=200, message="success", data=RecordActionSchema.from_orm(one_data)).json()


@router.post("/query/info", response_model=BaseResponse)
async def query_info(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Parse the incoming JSON data
    data = await request.json()
    data['proxies'] = {"http://": None, "https://": None}
    data['headers'] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/"
    }
    url = data.get("url")
    # You can process the data here
    print(f'data:{data}')
    print(f'url:{url}')
    aweme_id = await AwemeIdFetcher.get_aweme_id(data.get("url"))
    async with DouyinCrawler(data) as crawler:
        params = PostDetail(aweme_id=aweme_id)
        response = await crawler.fetch_post_detail(params)
        if response['status_code'] != 0:
            aweme_type: int = -1
        else:
            aweme_type: int = response['aweme_detail']['aweme_type']
        video: PostDetailFilter = PostDetailFilter(response)

    video_dict: dict = video._to_dict()
    print(f'time:{datetime.now()} response: {response}')
    logger.info(_("单个作品数据：{0}").format(video_dict))

    # 保存数据到数据库
    new_msg = RecordAction(
        record_id=str(uuid.uuid4()),
        input_url_params='',
        input_args=json.dumps(data),
        type='DY',
        mix_type=str(aweme_type),
        output_body=json.dumps(video_dict),
        visitor_id=data['vid'] if data['vid'] else 'anonymous',
        creator='dy_python_service',
        updater='dy_python_service',
        is_delete=False,
        is_finish=False
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    save_path: Path = create_user_folder(data, video.sec_user_id)
    logger.info(_("保存路径：{0}").format(save_path))
    print(f'start background task time:{datetime.now()}')
    background_tasks.add_task(process_download, data, video_dict, save_path, new_msg.record_id, db)
    print(f'end background task time:{datetime.now()}')
    return BaseResponse(code=200, message="success", data=RecordActionSchema.from_orm(new_msg)).json()


async def process_download(data: dict, video_dict: dict, save_path: Path, record_id: str, db: Session):
    """
    :param data: 传入的json数据，request body
    :param video_dict: 解析的dy信息
    :param save_path: 保存路径
    :param record_id: 数据库的id
    :param db: db-session
    :return: none
    """

    # 使用 DouyinDownloader 异步创建下载任务
    await DouyinDownloader(data).create_download_tasks(data, video_dict, save_path)

    # 根据 aweme_type 处理图片和视频上传
    if video_dict['aweme_type'] == 68:
        video_dict['upload_img_urls'] = upload_img_to_storage(str(save_path), video_dict['sec_user_id'])
    else:
        video_dict['upload_cover_url'] = upload_file_to_storage(str(save_path), data, video_dict['sec_user_id'],
                                                                '_cover.jpeg')
        video_dict['upload_video_url'] = upload_file_to_storage(str(save_path), data, video_dict['sec_user_id'],
                                                                '_video.mp4')

    # 更新数据库内容
    existing_msg = (db.query(RecordAction)
                    .filter(RecordAction.record_id == record_id)
                    .first())
    if existing_msg:
        existing_msg.output_body = json.dumps(video_dict)
        existing_msg.is_finish = True
        db.commit()
        db.refresh(existing_msg)


def upload_file_to_storage(real_path_str: str, data: dict, nickname: str, file_suffix: str):
    storage_type = os.environ.get('STORAGE_TYPE', 'default')
    storage = storage_factory.get_storage(storage_type)

    file_name = data.get("naming", "SET NAME") + file_suffix
    file_path = real_path_str + '/' + file_name
    logger.info(f"file_path: {file_path} file_name : {file_name}")
    now = datetime.now()  # 获取当前时间
    date_str = now.strftime("%Y%m%d")  # 将时间格式化为 YYYYMMDD 格式
    storage.upload(file_path, f'/dy/{date_str}/{nickname}/{file_name}',
                   meta_data=dict(cell_id='dy_' + file_suffix.split('.')[0]))
    os.remove(file_path)
    return f'{cdn_url}/dy/{date_str}/{nickname}/{file_name}'


def upload_img_to_storage(real_path_str: str, nickname: str) -> list:
    storage_type = os.environ.get('STORAGE_TYPE', 'default')
    storage = storage_factory.get_storage(storage_type)
    now = datetime.now()  # 获取当前时间
    date_str = now.strftime("%Y%m%d")  # 将时间格式化为 YYYYMMDD 格式
    return_array = []
    # 获取磁盘路径下的所有文件
    for file in os.listdir(real_path_str):
        if not file.startswith('.'):  # 忽略隐藏文件
            file_path = os.path.join(real_path_str, file)
            try:
                storage.upload(file_path, f'/dy/{date_str}/{nickname}/{file}',
                               meta_data=dict(cell_id='dy_' + os.path.splitext(file)[0]))
                os.remove(file_path)
                return_array.append(f'{cdn_url}/dy/{date_str}/{nickname}/{file}')
            except Exception as e:
                logger.error(f"Failed to upload or delete file {file_path}: {e}")
                continue
    return return_array


def create_user_folder(kwargs: dict, nickname) -> Path:
    # 创建基础路径
    temp_dir = tempfile.gettempdir()
    # base_path = Path(kwargs.get("path", "Download"))
    base_path = Path(temp_dir)

    # 添加下载模式和用户名
    user_path = (
            base_path / "douyin" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
    )

    # 获取绝对路径并确保它存在
    resolve_user_path = user_path.resolve()

    # 创建目录
    resolve_user_path.mkdir(parents=True, exist_ok=True)

    return resolve_user_path
