FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask boto3
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]