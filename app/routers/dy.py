import json

from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.model import PostDetail
from f2.apps.douyin.utils import (
    AwemeIdFetcher,
)
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.entity.base_response import BaseResponse
from app.entity.filter_model import PostDetailFilter
from f2.log.logger import logger
from f2.i18n.translator import _
from pathlib import Path

router = APIRouter()

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "device_web_cpu_core=8; device_web_memory_size=8; ttwid=1%7CZ7Zj5SecWZ2vBB3q2pyVNHVxytwaczKxxve0OI2G9_E%7C1722789513%7C4d7642643ce55da36ec2d6666351a2fa5b13115c93243a655e55fdb983943e00;UIFID_TEMP=04334f064e21198b2492613256b037a8641b36104347f0fcdf493d9e3675e398318558ac464d44f0386311521c18733cb0b2012f1309f15b52a784a337a29e7c6fd5ea66ca46ea79fac55f9ee4b492c7;douyin.com; s_v_web_id=verify_lzfse9r7_xekwZLO2_Bi52_48gY_AVIp_mH1viGlyTgVC; home_can_add_dy_2_desktop=%220%22;dy_swidth=2560; dy_sheight=1440; csrf_session_id=50db0a310110472f30f256bc1b619db3;xgplayer_user_id=574303257044; passport_csrf_token=3da088e91043f8b83736efc9e61d05f7;passport_csrf_token_default=3da088e91043f8b83736efc9e61d05f7; volume_info=%7B%22isMute%22%3Atrue%2C%22isUserMute%22%3Atrue%2C%22volume%22%3A0.6%7D;FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; xg_device_score=7.658235294117647;bd_ticket_guard_client_web_domain=2; fpk1=U2FsdGVkX19VnzQ1mfIkE+YKi6z8XjgYtJ1zS+m5/kuqvwglBjl9WG1T0JjEF8d+ip76D32Q64NZaTg7SVyPbA==;fpk2=6a23775729fd6c068d20d383cbe27f9b; UIFID=04334f064e21198b2492613256b037a8641b36104347f0fcdf493d9e3675e398318558ac464d44f0386311521c18733c4e0d8fc6271c054cf1a12b97a45b6dfa772f1f76841bab283ab12eda1fcebcfc3752d04b1ebbe944547a2d6aff69cfec7bc5ea489201c8a6901471b63bb068bb00517808c7987e54db99b13b9c767b7934a852b672c742a151038db00717a325fa90ed4e35eb938d14ef88cfbeda97f7;__ac_nonce=066b108ee0037945943ea; __ac_signature=_02B4Z6wo00f01MazsHQAAIDBilV.3JrBi3zGk7TAAFcj8f;strategyABtestKey=%221722878193.277%22; download_guide=%222%2F20240806%2F0%22;d_ticket=fb93d3108312a1cdd05796d767ee6a9da1955; passport_assist_user=CjxEMgcE3NIIawBTbctW54WrdPHKNdy5fzJl18zZPvmBllERjKfVqBqQa1WniHmDVBOMxyWtzVsuuNLjOlsaSgo8IoI5ZSPUNP5yrAdHNIy5ywb5KjB61taa-XkUJYyyPHGa_ZaJdWPtMocVH6-u88F0aQRWekP3krBVkFR7EIrM2A0Yia_WVCABIgED_zXOfQ%3D%3D;n_mh=DuBz1jrto4YM7DkRB1_oqvQ5kUhVBOzK-5g6cbDqsX0; sso_uid_tt=1f31a4fb0be172fd5ebf5d5aee8545ea;sso_uid_tt_ss=1f31a4fb0be172fd5ebf5d5aee8545ea; toutiao_sso_user=c95145af6dc105e174e9b20ec103c523;toutiao_sso_user_ss=c95145af6dc105e174e9b20ec103c523; sid_ucp_sso_v1=1.0.0-KDMxMTgwODg1MGQ3NWY4MTAzOTdmM2Q2NDdjYWZmOTJmZmFkM2JkMjAKHwjM4fn24QEQzJvEtQYY7zEgDDCRo_7IBTgGQPQHSAYaAmhsIiBjOTUxNDVhZjZkYzEwNWUxNzRlOWIyMGVjMTAzYzUyMw;ssid_ucp_sso_v1=1.0.0-KDMxMTgwODg1MGQ3NWY4MTAzOTdmM2Q2NDdjYWZmOTJmZmFkM2JkMjAKHwjM4fn24QEQzJvEtQYY7zEgDDCRo_7IBTgGQPQHSAYaAmhsIiBjOTUxNDVhZjZkYzEwNWUxNzRlOWIyMGVjMTAzYzUyMw;passport_auth_status=b5df7f702affe685b922c962120990b0%2C; passport_auth_status_ss=b5df7f702affe685b922c962120990b0%2C;uid_tt=6d7720dc6c31295b6dac51a7221cf38d; uid_tt_ss=6d7720dc6c31295b6dac51a7221cf38d;sid_tt=b8c3b3c3dc4c20fd0e87c9b7021adc50; sessionid=b8c3b3c3dc4c20fd0e87c9b7021adc50;sessionid_ss=b8c3b3c3dc4c20fd0e87c9b7021adc50; is_staff_user=false; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22;IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2560%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22;FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAk3m6xw-C1Rp29zVlEJlcq2zIjhSkd1XfwonBBdsjU20%2F1722960000000%2F0%2F1722879442524%2F0%22;passport_fe_beating_status=true; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=03a3af412fe912565dcbb39c93e0951c;__security_server_data_status=1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQk1SbUFmSklWWjZLc1hoVXh4NEo0aVhvSXhndFBxQ3A1RE84OEtjTnJPSW52ZlBoVEdVNy94VGh2a0diZ25YckQ5aFFiTUpWVlJNSEJZaHVDeGVCZWc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D;publish_badge_show_info=%220%2C0%2C0%2C1722879445679%22; sid_guard=b8c3b3c3dc4c20fd0e87c9b7021adc50%7C1722879446%7C5183993%7CFri%2C+04-Oct-2024+17%3A37%3A19+GMT;sid_ucp_v1=1.0.0-KGVlYjdlNGI1ZGNkOTZmYWM4MTI2YWM5MTJmMTZiYTJiNmIzZTMyMGEKGQjM4fn24QEQ1pvEtQYY7zEgDDgGQPQHSAQaAmxmIiBiOGMzYjNjM2RjNGMyMGZkMGU4N2M5YjcwMjFhZGM1MA;ssid_ucp_v1=1.0.0-KGVlYjdlNGI1ZGNkOTZmYWM4MTI2YWM5MTJmMTZiYTJiNmIzZTMyMGEKGQjM4fn24QEQ1pvEtQYY7zEgDDgGQPQHSAQaAmxmIiBiOGMzYjNjM2RjNGMyMGZkMGU4N2M5YjcwMjFhZGM1MA;biz_trace_id=d361b4ca; store-region=cn-tj; store-region-src=uid; odin_tt=f8bab7cff22f1bc648a1f8d34f1387c0cf669628a2db8850ee4efe6dcfb3adad622858a9f0e76fd664617c97b614dddc9a5dcfeafa7a637df468088cdf3e2833",
    "proxies": {"http://": None, "https://": None},
    "interval": "all",
    "url": "6.48 复制打开抖音，看看【番了个茄🍅的作品】这是什么神仙小狗？  https://v.douyin.com/irJy3pDV/ 02/17 n@Q.Kw PKW:/ "
}


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
