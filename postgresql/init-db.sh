#!/bin/bash
set -e

psql <<-EOSQL
    CREATE DATABASE $POSTGRES_DB;
EOSQL