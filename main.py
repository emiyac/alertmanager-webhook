import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from utils import (
    LOGGING_CONFIG,
    AlertManagerModel,
    ResponseModel,
    get_sign,
    logger,
    settings,
)

app = FastAPI(debug=settings.DEBUG)
templates = Jinja2Templates(directory=settings.TEMPLATE)
timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
grafana_url = (
    settings.GRAFANA_URL[-1]
    if settings.GRAFANA_URL.endswith("/")
    else settings.GRAFANA_URL
)


@app.get("/", response_model=ResponseModel, summary="health check")
def health_check():
    return {"code": "0000", "msg": "success", "data": None}


@app.post("/wechat", response_model=ResponseModel, summary="send msg to wechat webhook")
async def send_msg_to_wechat(
    items: AlertManagerModel,
    key: str = settings.WECHAT_WEBHOOK_KEY,
    tmpl: str = settings.WECHAT_TEMPLATE,
):
    logger.debug("items is: {}".format(items))
    if not key:
        raise Exception("environment WECHAT_WEBHOOK_KEY or request args key is not set")

    content = templates.get_template(tmpl).render(items=items, grafana_url=grafana_url)
    logger.debug("content is: {}".format(content))

    url = settings.WECHAT_WEBHOOK + key
    data = {"msgtype": "markdown", "markdown": {"content": content}}

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.json()
            logger.info(
                "tmpl={}, code={}, result={}".format(tmpl, resp_code, resp_data)
            )
    return {"code": "0000", "msg": "success", "data": resp_data}


@app.post(
    "/dingtalk", response_model=ResponseModel, summary="send msg to dingtalk webhook"
)
async def send_msg_to_dingtalk(
    items: AlertManagerModel,
    access_token: str = settings.DINGTALK_WEBHOOK_ACCESS_TOKEN,
    secret: str = settings.DINGTALK_WEBHOOK_SECRET,
    tmpl: str = settings.DINGTALK_TEMPLATE,
):
    logger.debug("items is: {}".format(items))
    if not access_token:
        raise Exception(
            "environment DINGTALK_WEBHOOK_ACCESS_TOKEN or request args access_token is not set"
        )
    if not secret:
        raise Exception(
            "environment DINGTALK_WEBHOOK_SECRET or request args secret is not set"
        )

    content = templates.get_template(tmpl).render(items=items, grafana_url=grafana_url)

    timestamp, sign = get_sign(secret=secret)
    url = settings.DINGTALK_WEBHOOK + "{}&timestamp={}&sign={}".format(
        access_token, timestamp, sign
    )
    data = {"msgtype": "markdown", "markdown": {"title": "title", "text": content}}

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.json()
            logger.info(
                "tmpl={}, code={}, result={}".format(tmpl, resp_code, resp_data)
            )
    return {"code": "0000", "msg": "success", "data": resp_data}


if __name__ == "__main__":
    uvicorn.run(app=app, log_config=LOGGING_CONFIG, host="0.0.0.0")
