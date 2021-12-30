FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY app /app
COPY lib /lib
COPY results /results

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :8080 --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 app:app
