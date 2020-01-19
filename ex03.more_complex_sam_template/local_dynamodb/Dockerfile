FROM python:3.6.8-alpine3.9

COPY scripts/ /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "create_resource.py"]