#!/bin/bash

HERE="$(unset CDPATH && cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$HERE"/.. && pwd)"

if ! test -f "$PROJECT_ROOT/.env"; then
    echo "Creating .env file..."
    cat <<'EOF' >"$PROJECT_ROOT/.env"
APP_BOT_TOKEN=bogon
APP_GUILD_ID=bogon
APP_CHANNEL_ID=bogon
APP_WEBHOOK_URL=bogon
EOF
fi

if ! test -f "$PROJECT_ROOT/config.toml"; then
    cat <<'EOF' >"$PROJECT_ROOT/config.toml"
[hockey]
teams = [
    "SEA",
    "EDM",
    "DET",
]

[soccer]
teams = ["SEA", "CHI"]

[football]
teams = ["DET"]
EOF

fi
