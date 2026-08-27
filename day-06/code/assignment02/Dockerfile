# Hardened container image for transactions-insight (Secure topic).
#
# The security goal here is a small image that runs as an unprivileged user, so a flaw in the app
# cannot easily become control of the host. Three habits do most of the work: build in one stage
# and copy only what runs into a slim final stage, run as a non-root user, and (at run time) make
# the root filesystem read only and drop every Linux capability.

# ---- Build stage: install dependencies into a virtual environment -------------------
FROM python:3.11-slim AS build

# Do not write .pyc files and do not buffer stdout, so logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry, then export a plain virtual environment. Copying only the manifest first lets
# Docker cache the dependency layer when only the source changes.
RUN pip install --no-cache-dir poetry==2.4.1
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true \
    && poetry install --only main --no-root

# Copy the source and build the package into the same virtual environment.
COPY src ./src
RUN poetry install --only main

# ---- Final stage: a slim runtime that carries only what it needs ---------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create an unprivileged user and group. Running as root inside a container is a real risk: a
# process escape would land with root on the host, so we never run the app as root.
RUN groupadd --system app && useradd --system --gid app --home-dir /app --no-create-home app

WORKDIR /app

# Copy the built virtual environment and the source from the build stage, owned by the app user.
COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --from=build --chown=app:app /app/src /app/src

# Drop to the unprivileged user for every command from here on.
USER app

EXPOSE 8000

# Run the API with uvicorn. The module path matches "transactions_insight.api:app".
CMD ["uvicorn", "transactions_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- Run-time hardening (applied by whoever runs the container) ---------------------
# The image is only half of the story; the run command tightens the rest. Recommended flags:
#
#   docker run \
#     --read-only \                     # a read-only root filesystem, so nothing can be written
#     --tmpfs /tmp \                    # give the app a small writable scratch area if it needs one
#     --cap-drop ALL \                  # drop every Linux capability; the app needs none of them
#     --security-opt no-new-privileges \  # a child process can never gain more privilege
#     transactions-insight
#
# read-only root plus dropped capabilities means a compromised process has almost no room to act:
# it cannot write the filesystem and it holds no privileged capability to abuse.
