#!/bin/sh
# Starts the AIR collector with a secret salt for PII redaction.
#
# The genaisafe processor hashes redacted values (emails, keys, ...) with a
# salt. If the salt is public, anyone can reverse those hashes by hashing a
# list of guesses, so it must stay secret.
#
#   - If GENAISAFE_SALT is set (e.g. in .env), that value is used.
#   - Otherwise a random salt is generated once and saved in the collector's
#     data volume, so hashes stay consistent across restarts.
set -eu

SALT_FILE=/data/vault/.genaisafe-salt

if [ -z "${GENAISAFE_SALT:-}" ]; then
  if [ ! -s "$SALT_FILE" ]; then
    umask 077
    head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n' > "$SALT_FILE"
    echo "collector-entrypoint: generated a new PII-redaction salt in $SALT_FILE"
  fi
  GENAISAFE_SALT=$(cat "$SALT_FILE")
fi
export GENAISAFE_SALT

exec air-collector --config=/etc/otel/collector.yaml
