FROM python:3.11-slim

WORKDIR /var/www/html/backend

ENV PYTHONPATH=/backend

COPY . /var/www/html/backend

RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir uvicorn

EXPOSE 5000 8000  

CMD ["python", "python_api.py"]
