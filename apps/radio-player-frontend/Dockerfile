FROM nginx:1.27-alpine

RUN apk add --no-cache gettext

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY docker/40-render-config.sh /docker-entrypoint.d/40-render-config.sh
COPY site/ /usr/share/nginx/html/

RUN chmod +x /docker-entrypoint.d/40-render-config.sh

ENV APP_TITLE="YourParty Radio"
ENV APP_TAGLINE="Listen live and stay close to the FraWo media lane."
ENV STREAM_URL="https://radio.example.invalid/live"
ENV STATUS_URL="https://status.example.invalid"
ENV SUPPORT_URL="https://frawo.example.invalid"

EXPOSE 8080
