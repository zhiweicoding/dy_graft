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

router = APIRouter()


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
        video = PostDetailFilter(response)

    logger.info(_("单个作品数据：{0}").format(video._to_dict()))

    save_path: Path = create_user_folder(data, video.sec_user_id)
    logger.info(_("保存路径：{0}").format(save_path))
    await DouyinDownloader(data).create_download_tasks(
        data, video._to_dict(), save_path
    )

    return BaseResponse(code=200, message="success", data=video._to_dict()).json()


def create_user_folder(kwargs: dict, nickname) -> Path:
    # 创建基础路径
    base_path = Path(kwargs.get("path", "Download"))

    # 添加下载模式和用户名
    user_path = (
            base_path / "douyin" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
    )

    # 获取绝对路径并确保它存在
    resolve_user_path = user_path.resolve()

    # 创建目录
    resolve_user_path.mkdir(parents=True, exist_ok=True)

    return resolve_user_path
