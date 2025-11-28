#!/bin/bash
set -euo pipefail

# Publish docker image to GitHub Container Registry (GHCR)
# Usage: ./scripts/publish_docker.sh [--tag TAG]

TAG=${1:-latest}
REPO=ghcr.io/adam-bouafia/logpress
IMAGE=logpress:${TAG}
GHCR_IMAGE=${REPO}:${TAG}

# Build the image
echo "🔨 Building Docker image: ${IMAGE}"
docker build -f deployment/Dockerfile -t ${IMAGE} .

# Tag for GHCR
echo "🏷 Tagging image as: ${GHCR_IMAGE}"
docker tag ${IMAGE} ${GHCR_IMAGE}

# Log in to GHCR (expects $GITHUB_TOKEN to be set as an env var)
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "⚠️  GITHUB_TOKEN not set. Please set GITHUB_TOKEN as environment variable (PAT with write:packages)"
  exit 1
fi

echo "🔐 Logging into GHCR as $(whoami)"
echo "${GITHUB_TOKEN}" | docker login ghcr.io -u $(whoami) --password-stdin

# Push the image
echo "🚀 Pushing ${GHCR_IMAGE}..."
docker push ${GHCR_IMAGE}

echo "✅ Push complete: ${GHCR_IMAGE}"

# Optional: clean local image (uncomment to enable)
# docker rmi ${IMAGE} ${GHCR_IMAGE}

exit 0
