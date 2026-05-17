#!/usr/bin/with-contenv bashio

bashio::log.info "Starting CavePut DB..."

# Export options for Python to read
export CAVEPUT_ZENPUT_EMAIL=$(bashio::config 'zenput_email')
export CAVEPUT_ZENPUT_PASSWORD=$(bashio::config 'zenput_password')
export CAVEPUT_DB_USERNAME=$(bashio::config 'db_username')
export CAVEPUT_DB_PASSWORD=$(bashio::config 'db_password')
export CAVEPUT_SYNC_HOUR=$(bashio::config 'sync_hour')
export CAVEPUT_SYNC_DOW=$(bashio::config 'sync_day_of_week')
export CAVEPUT_DATA_DIR=/data

cd /app
exec python3 -m caveputdb.main
