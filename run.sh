#!/bin/bash -ex

NAME=morst-bot
DB_LOCATION=/db
DB_NAME=morst_bot.db

docker build -t ${NAME} .
docker rm -f ${NAME} || true
docker run --name ${NAME} -d --restart=unless-stopped -e MORST_BOT_API_TOKEN=${MORST_BOT_API_TOKEN} -e MORST_BOT_DB_PATH=${DB_LOCATION}/${DB_NAME} -v ~/.morst_bot/:${DB_LOCATION} ${NAME}
docker logs -f ${NAME}
