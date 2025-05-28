#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE USER ${DB_USER:-videoflix} WITH PASSWORD '${DB_PASSWORD:-mein_sicheres_passwort}';

    SELECT 'CREATE DATABASE ${DB_NAME:-videoflix} OWNER ${DB_USER:-postgres}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME:-videoflix}')\gexec
    
    GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME:-videoflix_db} TO ${DB_USER:-videoflix};
    ALTER DATABASE ${DB_NAME:-videoflix_db} SET timezone TO 'Europe/Berlin';

    \c ${DB_NAME:-videoflix_db}
    GRANT ALL ON SCHEMA public TO ${DB_USER:-videoflix};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER:-videoflix};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER:-videoflix};
EOSQL