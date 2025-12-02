FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

EXPOSE 5000 8000  

CMD ["python", "python_api.py"]
