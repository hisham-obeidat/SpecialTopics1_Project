# ---- stage 1: build the wheel ----
FROM python:3.11-slim AS build
WORKDIR /src
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir build==1.2.2 && python -m build --wheel --outdir /dist

# ---- stage 2: runtime image with the model inside ----
FROM python:3.11-slim
WORKDIR /app
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl
COPY features.yaml /app/features.yaml
COPY artifacts/model.joblib /app/model/model.joblib

ARG MODEL_VERSION=cve-triage-1
ENV CVE_TRIAGE_MODEL=/app/model/model.joblib \
    CVE_TRIAGE_FEATURES=/app/features.yaml \
    CVE_TRIAGE_MODEL_VERSION=${MODEL_VERSION}

ENTRYPOINT ["python", "-m", "cve_triage.batch"]