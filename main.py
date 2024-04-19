import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import aiohttp

from utils.config import settings, logger, LOGGING_CONFIG
from utils.schema import AlertManagerModel
from utils.encrypt import get_sign

app = FastAPI(debug=settings.DEBUG)
tmpl = Jinja2Templates(directory=settings.TEMPLATE)
timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
grafana_url = settings.GRAFANA_URL[-1] if settings.GRAFANA_URL.endswith('/') else settings.GRAFANA_URL


@app.get("/")
def health_check():
    return {"code": "0000", "data": "health"}


@app.post("/wx")
async def send_msg_to_wx(items: AlertManagerModel):
    if not settings.WX_WEBHOOK:
        raise Exception("WX_WEBHOOK is not set")
    wx_tmpl = tmpl.get_template(settings.WX_TEMPLATE)
    content = wx_tmpl.render(items=items, grafana_url=grafana_url)
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    logger.debug(content)
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
    timestamp, sign = get_sign(settings.DINGTALK_SECRET)
    url = "{}&timestamp={}&sign={}".format(settings.DINGTALK_WEBHOOK, timestamp, sign)
    dingtalk_tmpl = tmpl.get_template(settings.DINGTALK_TEMPLATE)
    title = f"# 告警名称: {items.groupLabels.get('alertname')} \t告警状态: `{items.status}({len(items.alerts)})`"
    content = dingtalk_tmpl.render(items=items, grafana_url=grafana_url)
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content
        }
    }
    logger.debug(content)
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, timeout=timeout) as resp:
            resp_code = resp.status
            resp_data = await resp.json()
            logger.info("code={}, result={}".format(resp_code, resp_data))
    return {"code": "0000", "data": None}


if __name__ == '__main__':
    uvicorn.run(app=app, log_config=LOGGING_CONFIG, host="0.0.0.0")
