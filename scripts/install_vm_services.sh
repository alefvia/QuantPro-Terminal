#!/usr/bin/env bash
# QuantPro VM bootstrap. No Rithmic credentials are stored in this file.
set -euo pipefail

APP_DIR="/home/leviatalaia/QuantPro-Terminal"
PYTHON_BIN="/home/leviatalaia/QuantPro-Terminal/.venv/bin/python"
CONFIG_DIR="/etc/quantpro"

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

cat > /etc/systemd/system/quantpro-rithmic.path <<'UNIT'
[Unit]
Description=Start QuantPro Rithmic worker when its protected configuration exists

[Path]
PathExists=/etc/quantpro/rithmic.env
Unit=quantpro-rithmic.service

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now quantpro-api.service
systemctl enable quantpro-rithmic.service quantpro-rithmic.path
systemctl start quantpro-rithmic.path

echo "QuantPro API enabled. Rithmic worker will start automatically after protected configuration is present."
