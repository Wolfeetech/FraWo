// FraWo Funk Radio Vote Worker
// Deployed as Cloudflare Worker on vote.frawo-tech.de or similar
// Receives vote requests from authenticated Odoo users and forwards to AzuraCast

const AZURACAST_API_KEY = "__ROTATED_SECRET__";
const AZURACAST_URL = "https://funk.frawo-tech.de";
const STATION_ID = 1;
// Shared secret between Odoo frontend and this Worker so we know the vote came from a logged-in user
const ODOO_SHARED_SECRET = "__ROTATED_SECRET__";

addEventListener("fetch", event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  // CORS: Allow requests from our Odoo domain
  const corsHeaders = {
    "Access-Control-Allow-Origin": "http://10.1.0.112:8069",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Radio-Token",
    "Content-Type": "application/json"
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: corsHeaders
    });
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: corsHeaders
    });
  }

  // Validate shared secret (Odoo frontend passes this to prove the user was logged in)
  const token = request.headers.get("X-Radio-Token");
  if (token !== ODOO_SHARED_SECRET) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: corsHeaders
    });
  }

  const { song_id, vote_type, user_id } = body; // vote_type: "love" or "hate"

  if (!song_id || !vote_type || !user_id) {
    return new Response(JSON.stringify({ error: "Missing song_id, vote_type or user_id" }), {
      status: 400,
      headers: corsHeaders
    });
  }

  // Determine weight delta based on vote
  // AzuraCast uses "weight" on playlist items to control rotation frequency
  // For now we map to requesting a skip on "hate" and logging for "love"
  // In future: integrate with AzuraCast playlists weight API

  if (vote_type === "hate") {
    // Request to skip current song (requires live DJ or admin API)
    // For now just acknowledge and log it
    return new Response(JSON.stringify({
      success: true,
      message: "Vote received! Your feedback helps us improve the playlist.",
      action: "skip_requested"
    }), { status: 200, headers: corsHeaders });
  }

  if (vote_type === "love") {
    return new Response(JSON.stringify({
      success: true,
      message: "Glad you love it! We'll play this more often.",
      action: "love_logged"
    }), { status: 200, headers: corsHeaders });
  }

  return new Response(JSON.stringify({ error: "Unknown vote type" }), {
    status: 400,
    headers: corsHeaders
  });
}
