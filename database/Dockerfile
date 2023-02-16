FROM postgres:latest
ENV POSTGRES_PASSWORD=secret
ENV POSTGRES_USER=username
ENV POSTGRES_DB=database
ENV PGUSER=postgres
COPY init.sql /docker-entrypoint-initdb.d/init.sql
