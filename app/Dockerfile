FROM python:latest
WORKDIR /code
RUN pip install sqlalchemy
RUN pip install psycopg2
RUN pip install scrapy
COPY app.py app.py
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-u", "app.py"]