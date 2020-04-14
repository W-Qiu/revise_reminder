FROM postgres:12.1

COPY ./postgresql.conf /etc/postgresql/postgresql.conf
COPY ./data.dump /data.dump

# data directory = /var/lib/postgresql/data

# docker run -it --rm --env-file ../db-env -v postgres-data:/var/lib/postgresql/data postgres:dev