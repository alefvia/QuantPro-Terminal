#!/usr/bin/env bash
# QuantPro VM bootstrap. Rithmic credentials remain only in Secret Manager.
set -euo pipefail

APP_DIR="/home/leviatalaia/QuantPro-Terminal"
PYTHON_BIN="/home/leviatalaia/QuantPro-Terminal/.venv/bin/python"
CONFIG_DIR="/etc/quantpro"
METADATA="http://metadata.google.internal/computeMetadata/v1"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "QuantPro virtual environment not found: $PYTHON_BIN" >&2
  exit 1
fi

install -d -m 700 "$CONFIG_DIR"
if [ ! -s "$CONFIG_DIR/api.env" ]; then
  umask 077
  TOKEN="$($PYTHON_BIN -c 'import secrets; print(secrets.token_urlsafe(32))')"
  printf 'QUANTPRO_INGEST_TOKEN=%s\n' "$TOKEN" > "$CONFIG_DIR/api.env"
fi

metadata() {
  curl -fsS -H 'Metadata-Flavor: Google' "$METADATA/$1"
}

read_secret() {
  local secret_name="$1"
  local project token response
  project="$(metadata project/project-id)"
  token="$(metadata instance/service-accounts/default/token | "$PYTHON_BIN" -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"
  response="$(curl -fsS -H "Authorization: Bearer $token" "https://secretmanager.googleapis.com/v1/projects/$project/secrets/$secret_name/versions/latest:access")"
  printf '%s' "$response" | "$PYTHON_BIN" -c 'import base64,json,sys; print(base64.b64decode(json.load(sys.stdin)["payload"]["data"]).decode(), end="")'
}

# Build a root-readable configuration from Secret Manager at each boot.
# It is never committed and is only readable by root on the VM.
umask 077
RITHMIC_USER="$(read_secret quantpro-rithmic-user)"
RITHMIC_PASSWORD="$(read_secret quantpro-rithmic-password)"
printf 'RITHMIC_API_USER=%s\nRITHMIC_API_PASSWORD=%s\nRITHMIC_WSS_URL=wss://rituz00100.rithmic.com:443\nRITHMIC_KIT_DIR=/home/leviatalaia/rithmic-kit/extracted/0.90.0.0\nRITHMIC_CONTRACT_SYMBOL=MNQZ6\nQUANTPRO_FEED_URL=http://127.0.0.1:8000/feed/ingest\n' "$RITHMIC_USER" "$RITHMIC_PASSWORD" > "$CONFIG_DIR/rithmic.env"
chmod 600 "$CONFIG_DIR/rithmic.env"

cat > /etc/systemd/system/quantpro-api.service <<'UNIT'
[Unit]
Description=QuantPro local API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=leviatalaia
WorkingDirectory=/home/leviatalaia/QuantPro-Terminal
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/etc/quantpro/api.env
ExecStart=/home/leviatalaia/QuantPro-Terminal/.venv/bin/python -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

cat > /etc/systemd/system/quantpro-rithmic.service <<'UNIT'
[Unit]
Description=QuantPro Rithmic paper market-data worker
After=network-online.target quantpro-api.service
Wants=network-online.target
Requires=quantpro-api.service
ConditionPathExists=/etc/quantpro/rithmic.env

[Service]
Type=simple
User=leviatalaia
WorkingDirectory=/home/leviatalaia/QuantPro-Terminal
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/etc/quantpro/api.env
EnvironmentFile=/etc/quantpro/rithmic.env
ExecStart=/home/leviatalaia/QuantPro-Terminal/.venv/bin/python services/rithmic_mnq_worker.py
Restart=always
RestartSec=8

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now quantpro-api.service
systemctl enable --now quantpro-rithmic.service

echo "QuantPro services enabled. Rithmic credentials were loaded only from Secret Manager."
