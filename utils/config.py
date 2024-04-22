import logging
import logging.config

from pydantic import Field
from pydantic_settings import BaseSettings

from uvicorn.config import LOGGING_CONFIG

# 修改uvicorn默认的日志格式
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(name)s %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"] = '%(asctime)s %(name)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'


class Settings(BaseSettings):
    DEBUG: bool = Field(default=False, env="DEBUG", description="是否开启debug模式")
    TIMEOUT: int = Field(default=5, env="TIMEOUT", description="发送请求超时时间")
    GRAFANA_URL: str = Field(default="http://grafana:3000", env="GRAFANA_URL",
                             description="grafana地址,用于拼接告警信息跳转")
    TEMPLATE: str = Field(default="./templates", env="TEMPLATE", description="模板路径")
    # 企业微信机器人配置
    WX_WEBHOOK: str = Field(
        default="",
        env="WX_WEBHOOK", description="企业微信机器人webhook")
    WX_TEMPLATE: str = Field(default="wx.tmpl", env="WX_TEMPLATE", description="企业微信告警信息模板")
    # 钉钉机器人配置
    DINGTALK_WEBHOOK: str = Field(
        default="",
        env="DINGTALK_WEBHOOK", description="钉钉机器人webhook")
    DINGTALK_SECRET: str = Field(default="",
                                 env="DINGTALK_SECRET",
                                 description="加签,参考https://open.dingtalk.com/document/robots/customize-robot-security-settings")
    DINGTALK_TEMPLATE: str = Field(default="dingtalk.tmpl", env="DINGTALK_TEMPLATE", description="钉钉告警信息模板")


settings = Settings()
