#!/bin/bash

echo "stop container now..."
docker container stop webdav

echo "rm container now..."
docker container rm webdav

echo "upgrade image..."
docker pull manasalu/webdav:latest

echo "run container now..."
docker run --net=host \
    --name webdav -d \
    --restart unless-stopped \
    -v ${pwd}/logs:/app/logs \
    manasalu/webdav:latest \
    -t c0f5602cf959432787ad08728a9485e7 \
    --log=DEBUG


echo "container started."

