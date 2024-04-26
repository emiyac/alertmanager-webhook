from os import path

from pydantic import Field
from pydantic_settings import BaseSettings
from uvicorn.config import LOGGING_CONFIG

# 项目基础路径
base_dir = path.dirname(path.dirname(path.abspath(__file__)))

# 修改uvicorn默认的日志格式
LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
    "%(asctime)s %(name)s %(threadName)s - %(levelprefix)s %(message)s"
)
LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
    '%(asctime)s %(name)s %(threadName)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)


class Settings(BaseSettings):
    DEBUG: bool = Field(default=False, env="DEBUG", description="是否开启debug模式")
    TIMEOUT: int = Field(default=6, env="TIMEOUT", description="发送请求超时时间")
    GRAFANA_URL: str = Field(
        default="http://grafana:3000",
        env="GRAFANA_URL",
        description="grafana地址,用于拼接告警信息跳转",
    )
    TEMPLATE: str = Field(
        default=path.join(base_dir, "templates"), env="TEMPLATE", description="模板路径"
    )
    # 企业微信机器人配置
    WECHAT_WEBHOOK: str = Field(
        default="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=",
        env="WECHAT_WEBHOOK",
        description="企业微信机器人webhook地址",
    )
    WECHAT_WEBHOOK_KEY: str = Field(
        default="",
        env="WECHAT_WEBHOOK_KEY",
        description="企业微信机器人webhook的携带的请求参数key的值",
    )
    WECHAT_TEMPLATE: str = Field(
        default="wechat.tmpl",
        env="WECHAT_TEMPLATE",
        description="默认的企业微信告警信息模板",
    )
    # 钉钉机器人配置
    DINGTALK_WEBHOOK: str = Field(
        default="https://oapi.dingtalk.com/robot/send?access_token=",
        env="DINGTALK_WEBHOOK",
        description="钉钉机器人webhook地址",
    )
    DINGTALK_WEBHOOK_ACCESS_TOKEN: str = Field(
        default="",
        env="DINGTALK_WEBHOOK_ACCESS_TOKEN",
        description="钉钉机器人webhook携带的请求参数access_token的值",
    )
    DINGTALK_WEBHOOK_SECRET: str = Field(
        default="",
        env="DINGTALK_WEBHOOK_SECRET",
        description="加签,参考https://open.dingtalk.com/document/robots/customize-robot-security-settings",
    )
    DINGTALK_TEMPLATE: str = Field(
        default="dingtalk.tmpl",
        env="DINGTALK_TEMPLATE",
        description="默认的钉钉告警信息模板",
    )


settings = Settings()
