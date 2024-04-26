# AlertManager Webhook

<div>
  <a href="https://www.python.org/" target="_bank">
    <img src="https://img.shields.io/badge/Python-3.9-green?style=flat-square&logo=Python&logoColor=%233776AB" />
  </a>
  <a href="https://fastapi.tiangolo.com/" target="_bank">
    <img src="https://img.shields.io/badge/Fastapi-0.110.2-green?style=flat&logo=fastapi&logoColor=%23009688" />
  </a>
  <a href="https://jinja.palletsprojects.com/en/3.1.x/" target="_bank">
    <img src="https://img.shields.io/badge/Jinja2-3.1.3-green?style=flat&logo=jinja&logoColor=%23B41717" />
  </a>
  <a href="https://docs.aiohttp.org/en/stable/index.html" target="_bank">
    <img src="https://img.shields.io/badge/aiohttp-3.9.5-green?style=flat&logo=aiohttp&logoColor=%232C5BB4" />
  </a>
</div>


## 简介

`AlertManager Webhook` 是一个基于`FastApi`开发的插件，用于接收`AlertManager`组件发送的告警信息，并通过指定的模板渲染后发送至企业微信机器人或者钉钉机器人的`webhook`

## 默认的消息模板展示

企业微信消息：

![企业微信消息](./assets/wechat_firing.png) ![企业微信机器人消息格式展示](./assets/wechat_resolved.png)

钉钉消息：

![钉钉消息格式](./assets/dingtalk_firing.png) ![钉钉机器人消息格式展示](./assets/dingtalk_resolved.png)

## 配置和部署

### 自定义消息模板

所有模板默认放在`templates`目录下，可以通过环境变量`TEMPLATE`指定，模板使用`Jinja2`渲染，

模板语法请参考 :point_right: [Jinja2官方文档](https://jinja.palletsprojects.com/en/3.1.x/)

替换变量通过在模板中指定占位符`{{ }}`，例如

```shell
{{ items.alerts | length }}
{{ items.groupLabels.get('alertname') }}
{{ items.groupLabels['alertname'] }}
```

循环语法

```shell
{% for key, value in item.labels.items() %}
 {{ key }}: {{ value }}
{% endfor %}
```

分支语法
```shell
{% if items.status == "firing" %}
<font color="#FF8C00">
{% else %}
<font color="#3CB371">
{% endif %}
{{ items.status }}
</font>
```

空白控制，模板引擎默认不会对空白（空格、制表符、换行等）处理，可以在代码块开始或结束的位置放置特殊符号`-`来移除代码块前或代码块后的空白

```shell
{%- for key, value in item.labels.items() %}
> {{ key }}: {{ value }}
{%- endfor -%}
```

### alertmanager中的配置

```yaml
# receivers配置
receivers:
- name: 'wechat-webhook01'
  webhook_configs:
  - send_resolved: true
    # 使用默认的模板wechat.tmpl
    url: 'http://alertmanager-webhook:8000/wechat'

- name: 'wechat-webhook02'
  webhook_configs:
  - send_resolved: true
    # 使用key指定要发送的企业微信机器人,使用tmpl参数指定模板wechat01.tmpl
    url: 'http://alertmanager-webhook:8000/wechat?key?=xxx&tmpl=wechat01.tmpl'

- name: 'dingtalk-webhook01'
  webhook_configs:
  - send_resolved: true
    # 使用默认的模板dingtalk.tmpl
    url: 'http://alertmanager-webhook:8000/dingtalk'

- name: 'dingtalk-webhook02'
  webhook_configs:
  - send_resolved: true
    # # 使用access_token和secret指定要发送的企业微信机器人,使用tmpl参数指定模板dingtalk01.tmpl
    url: 'http://alertmanager-webhook:8000/dingtalk?access_token=xxx&secret=xxx&tmpl=dingtalk01.tmpl'
```

### 构建容器镜像

```bash
docker build -t alertmanager-webhook:v1 .
```
    
### 部署

环境变量说明：
* GRAFANA_URL: grafana访问的地址，用于拼接generatorURL，默认是http://grafana:3000
* WECHAT_WEBHOOK_KEY: 企业微信机器人webhook携带的key
* WECHAT_TEMPLATE: 默认的企业微信机器人的消息模板，默认是wechat.tmpl
* DINGTALK_WEBHOOK_ACCESS_TOKEN: 钉钉机器人webhook携带的access_token
* DINGTALK_WEBHOOK_SECRET: 钉钉机器人webhook的加签密钥
* DINGTALK_TEMPLATE: 默认的钉钉机器人的消息模板，默认是dingtalk.tmpl
* DEBUG: 是否开启调试模式，默认false

#### docker命令行部署

```bash
docker run -d --name alertmanager-webhook -e GRAFANA_URL="xxx" -e WECHAT_WEBHOOK_KEY="xxx" -e WECHAT_TEMPLATE="wechat01.tmpl" -e DINGTALK_WEBHOOK_ACCESS_TOKEN="xxx" -e DINGTALK_WEBHOOK_SECRET="xxx" -e DINGTALK_TEMPLATE="dingtalk01.tmpl" -e DEBUG=true -p 8000:8000 alertmanager-webhook:v1
```

#### docker-compose编排文件部署

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
      - GRAFANA_URL: xxx
      - WECHAT_WEBHOOK_KEY: xxx
      - WECHAT_TEMPLATE: wechat01.tmpl
      - DINGTALK_WEBHOOK_ACCESS_TOKEN: xxx
      - DINGTALK_WEBHOOK_SECRET: xxx
      - DINGTALK_TEMPLATE: dingtalk01.tmpl
      - DEBUG: true
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

#### kubernetes编排文件部署

```yaml
# 自定义的模板文件可以使用pvc,configMap或其他方式挂载到容器中，按实际需求配置
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: alertmanager-webhook
  name: alertmanager-webhook
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alertmanager-webhook
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: alertmanager-webhook
    spec:
      containers:
      - name: alertmanager-webhook
        image: harbor.example.com/common-test/alertmanager-webhook:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: GRAFANA_URL
          value: "xxx"
        - name: WECHAT_WEBHOOK_KEY
          value: "xxx"
        - name: WECHAT_TEMPLATE
          value: "wechat01.tmpl"
        - name: DINGTALK_WEBHOOK_ACCESS_TOKEN
          value: "xxx"
        - name: DINGTALK_WEBHOOK_SECRET
          value: "xxx"
        - name: DINGTALK_TEMPLATE
          value: "dingtalk01.tmpl"
        - name: DEBUG
          value: "true"
        resources: {}
status: {}
---
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: alertmanager-webhook
  name: alertmanager-webhook
spec:
  ports:
  - name: http
    port: 8000
    protocol: TCP
    targetPort: 8000
  selector:
    app: alertmanager-webhook
  type: NodePort
status:
  loadBalancer: {}
```