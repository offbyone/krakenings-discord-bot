set dotenv-load := true

@default:
    just --choose

bootstrap: env-template

env-template:
    scripts/ensure-env.sh

# Serve locally
serve:
    uv run python -m krakenings_discord_bot

build:
    uv build

clean:
    rm -rf dist/*

publish: clean build
    uvx twine upload dist/*

build-docker:
    docker build -t ghcr.io/offbyone/krakenings-discord-bot:latest .

sync:
    uv sync --dev

upgrade:
    uv sync --dev --refresh --upgrade

test:
    uv run pytest
