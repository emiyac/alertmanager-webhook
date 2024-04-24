# AlertManager Webhook

<div>
  <a href="https://www.python.org/" target="_bank">
    <img src="https://img.shields.io/badge/Python-3.9-green?style=flat-square&logo=Python&logoColor=%233776AB" />
  </a>
  <a href="https://fastapi.tiangolo.com/" target="_bank">
    <img src="https://img.shields.io/badge/Fastapi-0.110.2-green?style=flat&logo=fastapi&logoColor=%23009688" />
  </a>
  <a href="https://docs.jinkan.org/docs/jinja2/" target="_bank">
    <img src="https://img.shields.io/badge/Jinja2-3.1.3-green?style=flat&logo=jinja&logoColor=%23B41717" />
  </a>
  <a href="https://docs.aiohttp.org/en/stable/index.html" target="_bank">
    <img src="https://img.shields.io/badge/aiohttp-3.9.5-green?style=flat&logo=aiohttp&logoColor=%232C5BB4" />
  </a>
</div>


## 简介

`AlertManager Webhook` 是一个基于`FastApi`开发的插件，用于接收`AlertManager`组件发送的告警信息通过指定的模板渲染后发送至企业微信机器人或者钉钉机器人`webhook`

### 默认的消息模板

企业微信机器人消息：

![企业微信机器人消息格式展示](./assets/wechat_firing.png) ![企业微信机器人消息格式展示](./assets/wechat_resolved.png)

钉钉机器人消息：

![钉钉机器人消息格式展示](./assets/dingtalk_firing.png) ![钉钉机器人消息格式展示](./assets/dingtalk_resolved.png)

## 部署和使用

### 如何构建容器镜像

```bash
docker build -t alertmanager-webhook:v1 .
```
    
### 如何部署

环境变量说明：
* GRAFANA_URL: grafana访问的地址，用于拼接generatorURL，默认是http://grafana:3000
* DINGTALK_WEBHOOK: 钉钉机器人的webhook地址
* DINGTALK_SECRET: 钉钉机器人的密钥
* DINGTALK_TEMPLATE: 默认的钉钉机器人的消息模板，默认是dingtalk.tmpl
* WECHAT_WEBHOOK: 企业微信机器人的webhook地址
* WECHAT_TEMPLATE: 默认的企业微信机器人的消息模板，默认是wechat.tmpl
* DEBUG: 是否开启调试模式，默认false

#### docker部署

```bash
docker run -d --name alertmanager-webhook -e GRAFANA_URL="xxx" -e DINGTALK_WEBHOOK="xxx" -e DINGTALK_SECRET="xxx" -e DINGTALK_TEMPLATE="dingtalk.tmpl" -e WECHAT_WEBHOOK="xxx" -e WECHAT_TEMPLATE="wechat.tmpl" -e DEBUG=false -p 8000:8000 alertmanager-webhook:v1
```

#### docker-compose部署

```yaml
version: "3"

services:
  alertmanager-webhook:
    container_name: alertmanager-webhook
    hostname: alertmanager-webhook
    image: alertmanager-webhook:v1
    ports:
      - 8000:8000
    environment:
      - GRAFANA_URL=xxx
      - DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
      - DINGTALK_SECRET=xxx
      - DINGTALK_TEMPLATE=dingtalk.tmpl
      - WECHAT_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
      - WECHAT_TEMPLATE=wechat.tmpl
      - DEBUG=true
    volumes:
      - ./templates:/workspace/templates
    logging:
      driver: json-file
      options:
        max-size: 100m
        max-file: "3"
    networks:
      - lpg

networks:
  lpg:
    ipam:
      driver: default # default is bridge
      config:
        - subnet: 172.30.0.0/16
```

#### kubernetes部署

```yaml
# 自定义的模板文件可以使用存储或者configMap等方式挂载进容器中，看实际需求配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alertmanager-webhook
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alertmanager-webhook
  template:
    metadata:
      labels:
        app: alertmanager-webhook
    spec:
      containers:
        - name: alertmanager-webhook
          image: alertmanager-webhook:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: GRAFANA_URL
              value: "http://grafana:3000"
            - name: DINGTALK_WEBHOOK
              value: "https://oapi.dingtalk.com/robot/send?access_token=xxx"
            - name: DINGTALK_SECRET
              value: "xxx"
            - name: DINGTALK_TEMPLATE
              value: "dingtalk.tmpl"
            - name: WECHAT_WEBHOOK
              value: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
            - name: WECHAT_TEMPLATE
              value: "wechat.tmpl"
            - name: DEBUG
              value: "true"
---
apiVersion: v1
kind: Service
metadata:
  name: alertmanager-webhook
  namespace: default
spec:
  selector:
    app: alertmanager-webhook
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

### alertmanager中的配置

```yaml
# receivers配置，请求参数tmpl默认值是wechat.tmpl和dingtalk.tmpl，可以按照需求指定要使用的模板
receivers:
- name: 'dingtalk-webhook'
  webhook_configs:
  - send_resolved: true
    url: 'http://alertmanager-webhook:8000/dingtalk?tmpl=dingtalk01.tmpl'

receivers:
- name: 'wechat-webhook'
  webhook_configs:
  - send_resolved: true
    url: 'http://alertmanager-webhook:8000/dingtalk?tmpl=wechat01.tmpl'
```