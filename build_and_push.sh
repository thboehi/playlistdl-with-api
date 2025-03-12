#!/bin/bash
VERSION=$(cat app/VERSION | tr -d '\n\r')

echo "📦 Building Docker image: thomaboehi/playlistdlwithapi:$VERSION"
docker buildx build --platform linux/amd64 \
  -t thomaboehi/playlistdlwithapi:$VERSION \
  -t thomaboehi/playlistdlwithapi:latest \
  . --push

echo "✅ Done!"