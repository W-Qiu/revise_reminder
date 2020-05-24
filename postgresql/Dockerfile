FROM postgres:12.1

COPY ./postgresql.conf /etc/postgresql/postgresql.conf
COPY ./data.dump /data.dump

# data directory = /var/lib/postgresql/data

# RUN DIRECTLY
# docker run -it --rm --env-file ../db-env -v postgres-data:/var/lib/postgresql/data postgres:dev

# MANUALLY UPDATE USER PROGRESS
# docker-compose exec postgresql /bin/bash -c "psql -U postgres -d revise_reminder_db -c 'UPDATE users_customuser SET today_progress=0'"
