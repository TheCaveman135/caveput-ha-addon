ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip gcc musl-dev libffi-dev openssl-dev python3-dev

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY caveputdb/ ./caveputdb/
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
