FROM tiangolo/uvicorn-gunicorn:python3.11

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /

COPY ./app /app
# COPY ./templates /app/templates

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]