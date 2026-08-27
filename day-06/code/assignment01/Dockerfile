# A hardened container image for the telemetry-insight API.
#
# The security goals here are small and concrete:
#   1. Run as a non-root user, so a process breakout does not start as root.
#   2. Keep the image slim, so there is less software to attack.
#   3. Document the run-time hardening the operator should apply (read-only root
#      filesystem and dropped Linux capabilities), so the deployment is locked down too.

# A slim base keeps the attack surface small. Pin a specific version for repeatable builds.
FROM python:3.12-slim AS base

# Do not write .pyc files, and do not buffer stdout, so logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the project. We export a plain requirements list from Poetry at build time and
# install with pip, so the runtime image does not need Poetry itself.
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==2.4.1 \
    && poetry export --without-hashes --output requirements.txt \
    && pip install --no-cache-dir --requirement requirements.txt \
    && pip uninstall --yes poetry

# Copy the application source after dependencies, so a source-only change does not rebuild
# the dependency layer.
COPY src ./src

# Create an unprivileged user and hand it ownership of the app directory, then switch to it.
# Everything from here runs as "appuser", never as root.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# The API listens on 8000.
EXPOSE 8000

# Run the ASGI app with uvicorn.
CMD ["uvicorn", "telemetry_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Run-time hardening (applied by the operator, not baked into the image):
#
#   docker run \
#     --read-only \                     # mount the root filesystem read-only
#     --tmpfs /tmp \                     # give the app a small writable scratch area
#     --cap-drop ALL \                   # drop every Linux capability
#     --security-opt no-new-privileges \ # a child process can never gain more privileges
#     telemetry-insight
#
# The image already runs as a non-root user, so combined with a read-only root filesystem and
# no capabilities, a compromised process has very little it can do.
