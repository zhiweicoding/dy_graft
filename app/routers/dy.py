from pathlib import Path

from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.model import PostDetail
from f2.apps.douyin.utils import (
    AwemeIdFetcher,
)
from f2.i18n.translator import _
from f2.log.logger import logger
from fastapi import APIRouter, Request

from app.entity.base_response import BaseResponse
from app.entity.filter_model import PostDetailFilter
import tempfile
import os
import json
from app.storage import storage_factory
from datetime import datetime

router = APIRouter()

cdn_url = os.environ['CDN_URL']


@router.post("/query/info", response_model=BaseResponse)
async def receive_list(request: Request):
    # Parse the incoming JSON data
    data = await request.json()
    data['proxies'] = {"http://": None, "https://": None}
    url = data.get("url")
    # You can process the data here
    print(f'data:{data}')
    print(f'url:{url}')
    aweme_id = await AwemeIdFetcher.get_aweme_id(data.get("url"))
    async with DouyinCrawler(data) as crawler:
        params = PostDetail(aweme_id=aweme_id)
        response = await crawler.fetch_post_detail(params)
        video: PostDetailFilter = PostDetailFilter(response)

    video_dict: dict = video._to_dict()

    logger.info(_("单个作品数据：{0}").format(video_dict))

    save_path: Path = create_user_folder(data, video.sec_user_id)
    logger.info(_("保存路径：{0}").format(save_path))

    await DouyinDownloader(data).create_download_tasks(
        data, video_dict, save_path
    )

    video_dict['upload_cover_url'] = upload_file_to_storage(str(save_path), data, video.sec_user_id, '_cover.jpeg')
    video_dict['upload_video_url'] = upload_file_to_storage(str(save_path), data, video.sec_user_id, '_video.mp4')

    return BaseResponse(code=200, message="success", data=video_dict).json()


def upload_file_to_storage(real_path_str: str, data: dict, nickname: str, file_suffix: str):
    storage_type = os.environ.get('STORAGE_TYPE', 'default')
    storage = storage_factory.get_storage(storage_type)

    file_name = data.get("naming", "SET NAME") + file_suffix
    file_path = real_path_str + '/' + file_name
    logger.info(f"file_path: {file_path} file_name : {file_name}")
    now = datetime.now()  # 获取当前时间
    date_str = now.strftime("%Y%m%d")  # 将时间格式化为 YYYYMMDD 格式
    upload_resp = storage.upload(file_path, f'/dy/{date_str}/{nickname}/{file_name}',
                                 meta_data=dict(cell_id='dy_' + file_suffix.split('.')[0]))

    logger.info(f"File upload response: {json.dumps(upload_resp)}")
    os.remove(file_path)
    return f'{cdn_url}/dy/{date_str}/{nickname}/{file_name}'


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
