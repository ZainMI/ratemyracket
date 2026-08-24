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

Install Git, Docker Engine, the Docker Compose plugin, and `flock` on the home
server. Clone this repository into a dedicated deployment directory. A private
repository needs a GitHub deploy key or other non-interactive Git credential.

## Configure

From the repository root:

```bash
cp docker/.env.worker.example docker/.env.worker
chmod 600 docker/.env.worker
```

Edit `docker/.env.worker` with the same R2 and API credentials used by the
current Railway worker. The real file is ignored by Git.

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
0 2 * * * /absolute/path/to/RacketRating/docker/run-pipeline.sh >> /absolute/path/to/RacketRating/docker/pipeline.log 2>&1
```

Cron uses the home server's timezone. Check it with:

```bash
timedatectl
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
