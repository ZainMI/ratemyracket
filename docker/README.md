# Home-server pipeline worker

This folder packages the RacketRating ML pipeline as a one-shot Docker
container. The host scheduler starts it at 2:00 AM, and the runner:

1. prevents overlapping runs;
2. pulls the latest `main` branch from GitHub;
3. builds the worker image;
4. downloads the current pipeline state from R2;
5. runs the recent scrape, cleaning, feature, and training pipeline;
6. uploads the updated state to R2;
7. asks the Railway API to refresh; and
8. exits.

## Prerequisites

Install Git, Docker Engine, the Docker Compose plugin, `flock`, and Python 3 on
the home server. Clone this repository into a dedicated deployment directory.
A private repository needs a GitHub deploy key or other non-interactive Git
credential.

## Configure

From the repository root:

```bash
cp docker/.env.worker.example docker/.env.worker
chmod 600 docker/.env.worker
```

Edit `docker/.env.worker` with the same R2 and API credentials used by the
current Railway worker. The real file is ignored by Git.

For failure email, also set:

```env
MAIL_TO=zainmagdon@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=zainmagdon@gmail.com
SMTP_PASSWORD=your-google-app-password
SMTP_FROM=zainmagdon@gmail.com
```

Gmail requires a Google app password for SMTP; do not put your regular Google
password in this file. App passwords require 2-Step Verification on the Google
account. Keep `.env.worker` restricted with `chmod 600`.

Make the runner executable:

```bash
chmod +x docker/run-pipeline.sh
```

If the production branch is not `main`, set `PIPELINE_BRANCH` in the cron
command or the host environment.

## Test manually

Run this from anywhere:

```bash
/absolute/path/to/RacketRating/docker/run-pipeline.sh
```

The repository checkout must be clean enough for `git pull --ff-only` to
advance it. Keep this as a dedicated deployment clone rather than editing files
directly on the server.

## Schedule at 2:00 AM

Open the home server user's crontab:

```bash
crontab -e
```

Add the following, replacing the repository path:

```cron
0 2 * * * /absolute/path/to/RacketRating/docker/run-pipeline.sh >/dev/null 2>&1
```

Cron uses the home server's timezone. Check it with:

```bash
timedatectl
```

## Logs and failure email

Every run writes a timestamped log under `docker/logs/`, including failures
during Git pull, image build, and container execution. Logs are retained for 30
days by default.

```bash
ls -lt docker/logs/
tail -f docker/logs/latest.log
```

Override retention in the cron command if needed:

```cron
PIPELINE_LOG_RETENTION_DAYS=60
```

On failure, the runner emails the configured recipient with the exit code, log
path, and final 200 log lines. To test email without waiting for a real pipeline
failure:

```bash
python3 docker/send_failure_email.py \
  --env-file docker/.env.worker \
  --log-file docker/logs/latest.log \
  --exit-code 1
```

## Useful commands

Build without running:

```bash
docker compose --project-directory docker -f docker/docker-compose.worker.yml build pipeline
```

Run without pulling GitHub first:

```bash
docker compose --project-directory docker -f docker/docker-compose.worker.yml run --rm pipeline
```

Override the Git branch for one run:

```bash
PIPELINE_BRANCH=production docker/run-pipeline.sh
```

## Player corrections

`backend/ml/data/player_corrections.csv` is committed with the application
code. The pipeline also synchronizes `ml/data` with R2, so keep the R2 copy in
sync or exclude that configuration file from R2 synchronization if GitHub
should remain its only source of truth.
