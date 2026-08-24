#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BRANCH="${PIPELINE_BRANCH:-main}"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.worker.yml"
ENV_FILE="${SCRIPT_DIR}/.env.worker"
LOCK_FILE="${PIPELINE_LOCK_FILE:-/tmp/racketrating-pipeline.lock}"
LOG_DIR="${PIPELINE_LOG_DIR:-${SCRIPT_DIR}/logs}"
LOG_RETENTION_DAYS="${PIPELINE_LOG_RETENTION_DAYS:-30}"
RUN_TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
LOG_FILE="${LOG_DIR}/pipeline-${RUN_TIMESTAMP}.log"

mkdir -p "${LOG_DIR}"
touch "${LOG_FILE}"
ln -sfn "$(basename "${LOG_FILE}")" "${LOG_DIR}/latest.log"

# Save output on disk while continuing to display it during manual runs.
exec > >(tee -a "${LOG_FILE}") 2>&1

finish_run() {
  local exit_code=$?
  trap - EXIT

  if [[ ${exit_code} -ne 0 ]]; then
    echo "Pipeline worker failed with exit code ${exit_code}."
    if command -v python3 >/dev/null 2>&1; then
      python3 "${SCRIPT_DIR}/send_failure_email.py" \
        --env-file "${ENV_FILE}" \
        --log-file "${LOG_FILE}" \
        --exit-code "${exit_code}" || \
        echo "Warning: failure email could not be sent."
    else
      echo "Warning: python3 is unavailable; failure email was not sent."
    fi
  fi

  if [[ "${LOG_RETENTION_DAYS}" =~ ^[0-9]+$ ]]; then
    find "${LOG_DIR}" -maxdepth 1 -type f \
      -name 'pipeline-*.log' -mtime "+${LOG_RETENTION_DAYS}" -delete
  else
    echo "Warning: invalid PIPELINE_LOG_RETENTION_DAYS; logs not pruned."
  fi

  exit "${exit_code}"
}
trap finish_run EXIT

echo "Log file: ${LOG_FILE}"
echo "Pipeline worker started at $(date --iso-8601=seconds 2>/dev/null || date)."

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "A RacketRating pipeline run is already in progress."
  exit 0
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.worker.example and add credentials."
  exit 1
fi

echo "Updating ${REPO_DIR} from origin/${BRANCH}..."
git -C "${REPO_DIR}" fetch origin "${BRANCH}"
git -C "${REPO_DIR}" pull --ff-only origin "${BRANCH}"

echo "Building pipeline worker..."
docker compose --project-directory "${SCRIPT_DIR}" \
  -f "${COMPOSE_FILE}" build pipeline

echo "Running pipeline worker..."
docker compose --project-directory "${SCRIPT_DIR}" \
  -f "${COMPOSE_FILE}" run --rm pipeline

echo "Pipeline worker completed."
