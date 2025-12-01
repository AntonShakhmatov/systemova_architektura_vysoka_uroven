FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

EXPOSE 5000 8000  

# CMD по умолчанию не так важен, потому что его переопределит docker-compose,
# но пусть будет какая-то дефолтная команда
CMD ["python", "python_api.py"]
