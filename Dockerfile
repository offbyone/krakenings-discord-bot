# syntax=docker/dockerfile:1.9
FROM python:3.13-bookworm AS build

# The following does not work in Podman unless you build in Docker
# compatibility mode: <https://github.com/containers/podman/issues/8477>
# You can manually prepend every RUN script with `set -ex` too.
SHELL ["sh", "-exc"]

### Start Build Prep.
### This should be a separate build container for better reuse.

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    rsync \
    ca-certificates \
    curl
EOT

# Security-conscious organizations should package/review uv themselves.
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/app` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_PREFERENCE=system \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app

### End Build Prep -- this is where your Dockerfile should start.

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

# Prepare a virtual environment.
# This is cached until the Python version changes above.
#
# Note: This will not succeed if you are referencing nomnom's development version
# unless you re-build the uv lock without sources and with prereleases.
RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync \
    --frozen \
    --no-dev \
    --no-sources \
    --no-install-project
EOT

# Now install the APPLICATION from `/src` without any dependencies.
# `/src` will NOT be copied into the runtime container.
# LEAVE THIS OUT if your application is NOT a proper Python package.
COPY . /src
RUN --mount=type=cache,target=/root/.cache <<EOT
cd /src
uv sync --no-editable
EOT

##########################################################################

FROM python:3.13-bookworm AS run
SHELL ["sh", "-exc"]

# add the application virtualenv to search path.
ENV PATH=/app/bin:$PATH

# Don't run your app as root.
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

ENTRYPOINT ["/usr/bin/tini", "-v"]
# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

# Note how the runtime dependencies differ from build-time ones.
# Notably, there is no uv either!
RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    ca-certificates \
    gettext \
    python-is-python3

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Copy the pre-built `/app` directory to the runtime container
# and change the ownership to user app and group app in one step.
COPY --from=build --chown=app:app /app /app

VOLUME /staticfiles

USER app
WORKDIR /app

# if I need a web endpoint
# EXPOSE 8000

CMD ["python", "-m", "krakenings_discord_bot"]
