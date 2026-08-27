# A hardened container image for reviews-insight (the secure topic).
#
# The security ideas here are: run as a non-root user, keep the image small, and let the
# orchestrator lock the running container down further at run time. The comments call out the
# run-time controls (read-only root filesystem, dropped Linux capabilities) that belong in the
# deployment manifest rather than in the image itself.

# A slim base keeps the attack surface small: fewer packages means fewer known vulnerabilities.
FROM python:3.11-slim AS base

# Predictable Python behavior in a container: no .pyc writes, unbuffered stdout for live logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached when only the source changes.
COPY pyproject.toml README.md* ./
COPY src ./src

# Install the application. --no-cache-dir keeps the image from carrying pip's download cache.
RUN pip install --no-cache-dir .

# Create an unprivileged user and run as it. A process that is not root cannot, for example,
# write outside its allowed paths or bind a privileged port, so a bug or an exploit is contained.
# --create-home gives it a home directory; --system marks it as a non-login service account.
RUN useradd --create-home --system --uid 10001 appuser
USER appuser

# The service listens on 8000. Nothing above binds a privileged (<1024) port, on purpose.
EXPOSE 8000

# Run-time hardening is applied by the orchestrator, not baked in here. In a Kubernetes
# securityContext (or the equivalent docker run flags) the deployment should set:
#   - a read-only root filesystem (docker run --read-only), so the code cannot be modified in
#     place and no unexpected file can be written outside an explicit writable volume,
#   - all Linux capabilities dropped (docker run --cap-drop=ALL), so the container keeps only
#     the privileges it truly needs,
#   - no privilege escalation (allowPrivilegeEscalation: false).
# Keeping these at run time lets one image be deployed under one consistent, auditable policy.

CMD ["uvicorn", "reviews_insight.api:app", "--host", "0.0.0.0", "--port", "8000"]
