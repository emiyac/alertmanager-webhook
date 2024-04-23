FROM python:3.9-alpine
WORKDIR /workspace
RUN set -ex && \
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --update --no-cache --virtual .fetch-deps tzdata && \
    cp -a /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone && \
    apk del --no-network .fetch-deps
COPY . /workspace/
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ENTRYPOINT ["python", "main.py"]