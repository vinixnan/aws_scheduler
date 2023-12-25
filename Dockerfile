FROM python:3.11-slim

ENV AWS_ACCESS_KEY_ID "AKIAVVC74HRDQZN2M2EQ"
ENV AWS_SECRET_ACCESS_KEY "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"
ENV AWS_DEFAULT_REGION "us-east-1"

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
RUN cd /code/app/tests && python -m pytest