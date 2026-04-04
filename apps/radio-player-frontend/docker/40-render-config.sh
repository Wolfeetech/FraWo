#!/bin/sh
set -eu

envsubst '${APP_TITLE} ${APP_TAGLINE} ${STREAM_URL} ${STATUS_URL} ${SUPPORT_URL}' \
  < /usr/share/nginx/html/config.template.js \
  > /usr/share/nginx/html/config.js
