import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from utils import LOGGING_CONFIG, AlertManagerModel, get_sign, logger, settings

app = FastAPI(debug=settings.DEBUG)
templates = Jinja2Templates(directory=settings.TEMPLATE)
timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
grafana_url = (
    settings.GRAFANA_URL[-1]
    if settings.GRAFANA_URL.endswith("/")
    else settings.GRAFANA_URL
)


@app.get("/", summary="health check")
def health_check():
    return {"code": "0000", "data": "health"}


@app.post("/wechat", summary="send msg to wechat webhook")
async def send_msg_to_wechat(
    items: AlertManagerModel, tmpl: str = settings.WECHAT_TEMPLATE
):
    logger.debug("items is: {}".format(items))
    if not settings.WECHAT_WEBHOOK:
        raise Exception("WECHAT_WEBHOOK is not set")
    content = templates.get_template(tmpl).render(items=items, grafana_url=grafana_url)
    logger.debug("content is: {}".format(content))
    data = {"msgtype": "markdown", "markdown": {"content": content}}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=settings.WX_WEBHOOK, json=data, timeout=timeout
        ) as resp:
            resp_code = resp.status
            resp_data = await resp.text()
            logger.info(
                "tmpl={}, code={}, result={}".format(tmpl, resp_code, resp_data)
            )
    return {"code": "0000", "data": None}


@app.post("/dingtalk", summary="send msg to dingtalk webhook")
async def send_msg_to_dingtalk(
    items: AlertManagerModel, tmpl: str = settings.DINGTALK_TEMPLATE
):
    logger.debug("items is: {}".format(items))
    if not settings.DINGTALK_WEBHOOK or not settings.DINGTALK_SECRET:
        raise Exception("DINGTALK_WEBHOOK or DINGTALK_SECRET is not set")
    content = templates.get_template(tmpl).render(items=items, grafana_url=grafana_url)
    logger.debug("content is: {}".format(content))
    timestamp, sign = get_sign(settings.DINGTALK_SECRET)
    url = "{}&timestamp={}&sign={}".format(settings.DINGTALK_WEBHOOK, timestamp, sign)
    title = "自定义告警"
    data = {"msgtype": "markdown", "markdown": {"title": title, "text": content}}

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.text()
            logger.info(
                "tmpl={}, code={}, result={}".format(tmpl, resp_code, resp_data)
            )
    return {"code": "0000", "data": None}


if __name__ == "__main__":
    uvicorn.run(app=app, log_config=LOGGING_CONFIG, host="0.0.0.0")
