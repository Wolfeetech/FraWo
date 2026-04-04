const cfg = window.APP_CONFIG || {};

const byId = (id) => document.getElementById(id);

const title = byId("app-title");
const tagline = byId("app-tagline");
const listenLink = byId("listen-link");
const statusLink = byId("status-link");
const supportLink = byId("support-link");
const player = byId("player");
const streamUrl = byId("stream-url");

document.title = cfg.appTitle || document.title;
title.textContent = cfg.appTitle || "YourParty Radio";
tagline.textContent = cfg.appTagline || "Listen live and stay close to the FraWo media lane.";
listenLink.href = cfg.streamUrl || "#player";
statusLink.href = cfg.statusUrl || "#";
supportLink.href = cfg.supportUrl || "#";
player.src = cfg.streamUrl || "";
streamUrl.textContent = cfg.streamUrl ? `Stream: ${cfg.streamUrl}` : "Stream URL not configured yet.";
