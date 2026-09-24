FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home appuser
COPY app.py seed.py ./
COPY web ./web
RUN mkdir /app/data && chown -R appuser:appuser /app
USER appuser
EXPOSE 8010
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010", "--no-access-log"]
