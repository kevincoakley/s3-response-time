FROM  python:3.8-alpine

RUN mkdir /code /config
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "/code/s3_response_time.py", "-c"]

COPY s3_response_time.py requirements.txt /code/


