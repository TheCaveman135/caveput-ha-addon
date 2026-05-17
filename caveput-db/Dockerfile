FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY caveputdb/ ./caveputdb/
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
