#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BRANCH="${PIPELINE_BRANCH:-main}"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.worker.yml"
ENV_FILE="${SCRIPT_DIR}/.env.worker"
LOCK_FILE="${PIPELINE_LOCK_FILE:-/tmp/racketrating-pipeline.lock}"

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
