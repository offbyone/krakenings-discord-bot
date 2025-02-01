#!/bin/bash

HERE="$(unset CDPATH && cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$HERE"/.. && pwd)"

if test -f "$PROJECT_ROOT/.env"; then
    exit 0
fi

echo "Creating .env file..."
cat <<EOF >"$PROJECT_ROOT/.env"
BOT_TOKEN=bogon
GUILD_ID=bogon
EOF
