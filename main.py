import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import aiohttp

from utils import settings, LOGGING_CONFIG, get_sign, AlertManagerModel, logger

app = FastAPI(debug=settings.DEBUG)
templates = Jinja2Templates(directory=settings.TEMPLATE)
timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
grafana_url = settings.GRAFANA_URL[-1] if settings.GRAFANA_URL.endswith('/') else settings.GRAFANA_URL


@app.get("/")
def health_check():
    return {"code": "0000", "data": "health"}


@app.post("/wx")
async def send_msg_to_wx(items: AlertManagerModel):
    if not settings.WX_WEBHOOK:
        raise Exception("WX_WEBHOOK is not set")
    content = templates.get_template(settings.WX_TEMPLATE).render(items=items, grafana_url=grafana_url)
    logger.debug(content)
    data = {"msgtype": "markdown", "markdown": {"content": content}}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=settings.WX_WEBHOOK, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.json()
            logger.info("code={}, result={}".format(resp_code, resp_data))
    return {"code": "0000", "data": None}


@app.post("/dingtalk")
async def send_msg_to_dingtalk(items: AlertManagerModel):
    if not settings.DINGTALK_WEBHOOK or not settings.DINGTALK_SECRET:
        raise Exception("DINGTALK_WEBHOOK or DINGTALK_SECRET is not set")
    content = templates.get_template(settings.DINGTALK_TEMPLATE).render(items=items, grafana_url=grafana_url)
    logger.debug(content)
    timestamp, sign = get_sign(settings.DINGTALK_SECRET)
    url = "{}&timestamp={}&sign={}".format(settings.DINGTALK_WEBHOOK, timestamp, sign)
    title = "自定义告警"
    data = {"msgtype": "markdown", "markdown": {"title": title, "text": content}}

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.json()
            logger.info("code={}, result={}".format(resp_code, resp_data))
    return {"code": "0000", "data": None}


if __name__ == '__main__':
    uvicorn.run(app=app, log_config=LOGGING_CONFIG, host="0.0.0.0")
