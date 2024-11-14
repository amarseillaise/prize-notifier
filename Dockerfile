FROM python:3.11-slim

WORKDIR /prize-notifier

COPY ./app ./prize-notifier
COPY ./bot ./prize-notifier
COPY ./external_sources_service ./prize-notifier
COPY ./api.env ./prize-notifier
COPY ./bot.env ./prize-notifier
COPY ./init_service.py ./prize-notifier
COPY ./start_api.py ./prize-notifier
COPY ./start_bot.py ./prize-notifier
COPY ./requirements.txt ./prize-notifier
COPY ./start.sh ./prize-notifier

RUN pip install --no-cache-dir --upgrade -r ./prize-notifier/requirements.txt

CMD ["./start.sh"]