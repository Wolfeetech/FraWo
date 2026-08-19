import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Full QWeb page - premium design with native Odoo login detection
page_html = '''<?xml version="1.0"?>
<t name="FraWo Funk Radio" t-name="website.frawo_radio_page">
    <t t-call="website.layout">
        <t t-set="head_custom_js">
            <link rel="preconnect" href="https://fonts.googleapis.com"/>
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&amp;family=Space+Mono:wght@400;700&amp;display=swap" rel="stylesheet"/>
        </t>
        <div id="wrap">
            <style>
                :root {
                    --acid: #B9FF00;
                    --deep: #0A0A0A;
                    --surface: #111111;
                    --card: #1A1A1A;
                    --border: #2A2A2A;
                    --muted: #555;
                    --text: #FAFAFA;
                }
                body { background: var(--deep) !important; font-family: \'Space Grotesk\', sans-serif; }
                .o_header_standard { background: var(--deep) !important; border-bottom: 1px solid var(--border) !important; }
                #frawo-radio { min-height: 100vh; background: var(--deep); color: var(--text); padding: 0; }

                /* HERO */
                .radio-hero {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    min-height: 100vh;
                    gap: 0;
                }
                .radio-hero-left {
                    background: var(--surface);
                    padding: 80px 60px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    border-right: 1px solid var(--border);
                    position: relative;
                    overflow: hidden;
                }
                .radio-hero-left::before {
                    content: \'FRAWO FUNK\';
                    position: absolute;
                    font-size: 200px;
                    font-weight: 900;
                    color: rgba(255,255,255,0.015);
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-15deg);
                    white-space: nowrap;
                    pointer-events: none;
                    font-family: \'Space Mono\', monospace;
                }
                .radio-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: var(--card);
                    border: 1px solid var(--border);
                    border-radius: 100px;
                    padding: 8px 16px;
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                    color: var(--acid);
                    font-weight: 600;
                    margin-bottom: 40px;
                    width: fit-content;
                }
                .live-dot {
                    width: 8px;
                    height: 8px;
                    background: var(--acid);
                    border-radius: 50%;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.4; transform: scale(0.8); }
                }
                .radio-logo {
                    font-size: 88px;
                    font-weight: 700;
                    line-height: 0.9;
                    letter-spacing: -4px;
                    margin-bottom: 24px;
                    font-family: \'Space Mono\', monospace;
                }
                .radio-logo span { color: var(--acid); }
                .radio-tagline {
                    font-size: 16px;
                    color: var(--muted);
                    font-weight: 400;
                    margin-bottom: 60px;
                    letter-spacing: 1px;
                }

                /* PLAYER */
                .player-card {
                    background: var(--card);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 28px;
                    margin-bottom: 20px;
                    position: relative;
                }
                .now-playing-label {
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                    color: var(--muted);
                    margin-bottom: 16px;
                }
                .now-playing-meta {
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 24px;
                }
                .cover-art {
                    width: 72px;
                    height: 72px;
                    border-radius: 8px;
                    object-fit: cover;
                    background: var(--border);
                    flex-shrink: 0;
                    transition: opacity 0.3s;
                }
                .cover-art.loading { opacity: 0.3; }
                .track-info { flex: 1; min-width: 0; }
                .track-title {
                    font-size: 20px;
                    font-weight: 700;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-bottom: 4px;
                }
                .track-artist {
                    font-size: 14px;
                    color: var(--muted);
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .track-album {
                    font-size: 12px;
                    color: var(--border);
                    margin-top: 4px;
                }

                /* CONTROLS */
                .player-controls {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                }
                .play-btn {
                    width: 56px;
                    height: 56px;
                    border-radius: 50%;
                    background: var(--acid);
                    color: var(--deep);
                    border: none;
                    font-size: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: transform 0.15s, box-shadow 0.15s;
                    flex-shrink: 0;
                }
                .play-btn:hover { transform: scale(1.08); box-shadow: 0 0 30px rgba(185,255,0,0.4); }
                .play-btn:active { transform: scale(0.96); }
                .volume-container { display: flex; align-items: center; gap: 10px; flex: 1; }
                .volume-icon { color: var(--muted); font-size: 14px; }
                input[type=range] {
                    -webkit-appearance: none;
                    width: 100%;
                    height: 3px;
                    background: var(--border);
                    border-radius: 2px;
                    outline: none;
                }
                input[type=range]::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    width: 14px;
                    height: 14px;
                    background: var(--acid);
                    border-radius: 50%;
                    cursor: pointer;
                }

                /* WAVEFORM ANIMATION */
                .waveform {
                    display: flex;
                    align-items: center;
                    gap: 3px;
                    height: 24px;
                    margin-left: auto;
                }
                .waveform-bar {
                    width: 3px;
                    background: var(--acid);
                    border-radius: 2px;
                    animation: wave 1.2s ease-in-out infinite;
                    opacity: 0;
                    transition: opacity 0.3s;
                }
                .waveform-bar:nth-child(2) { animation-delay: 0.1s; }
                .waveform-bar:nth-child(3) { animation-delay: 0.2s; }
                .waveform-bar:nth-child(4) { animation-delay: 0.3s; }
                .waveform-bar:nth-child(5) { animation-delay: 0.4s; }
                .waveform.active .waveform-bar { opacity: 1; }
                @keyframes wave {
                    0%, 100% { height: 4px; }
                    50% { height: 20px; }
                }

                /* VOTING */
                .vote-section {
                    background: var(--card);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 20px 28px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 16px;
                }
                .vote-label {
                    font-size: 13px;
                    color: var(--muted);
                    font-weight: 500;
                }
                .vote-buttons { display: flex; gap: 12px; }
                .vote-btn {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 10px 20px;
                    border-radius: 100px;
                    border: 1px solid var(--border);
                    background: transparent;
                    color: var(--text);
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-family: \'Space Grotesk\', sans-serif;
                }
                .vote-btn:hover { border-color: var(--acid); color: var(--acid); transform: translateY(-2px); }
                .vote-btn.love:hover { box-shadow: 0 4px 20px rgba(185,255,0,0.2); }
                .vote-btn.hate:hover { border-color: #FF4444; color: #FF4444; box-shadow: 0 4px 20px rgba(255,68,68,0.15); }
                .vote-btn.voted-love { background: rgba(185,255,0,0.1); border-color: var(--acid); color: var(--acid); }
                .vote-btn.voted-hate { background: rgba(255,68,68,0.1); border-color: #FF4444; color: #FF4444; }
                .vote-toast {
                    position: fixed;
                    bottom: 30px;
                    left: 50%;
                    transform: translateX(-50%) translateY(100px);
                    background: var(--card);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 14px 24px;
                    font-size: 14px;
                    font-weight: 500;
                    z-index: 9999;
                    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
                    pointer-events: none;
                }
                .vote-toast.show { transform: translateX(-50%) translateY(0); }

                /* RIGHT SIDE */
                .radio-hero-right {
                    background: var(--deep);
                    padding: 80px 60px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .section-title {
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                    color: var(--muted);
                    margin-bottom: 32px;
                    font-weight: 600;
                }
                .community-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 32px;
                    margin-bottom: 20px;
                }
                .community-card h3 {
                    font-size: 22px;
                    font-weight: 700;
                    margin-bottom: 12px;
                }
                .community-card p {
                    font-size: 14px;
                    color: var(--muted);
                    line-height: 1.6;
                    margin-bottom: 24px;
                }
                .btn-acid {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: var(--acid);
                    color: var(--deep);
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 14px;
                    text-decoration: none;
                    transition: transform 0.15s, box-shadow 0.15s;
                    border: none;
                    cursor: pointer;
                    font-family: \'Space Grotesk\', sans-serif;
                }
                .btn-acid:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(185,255,0,0.35); color: var(--deep); text-decoration: none; }
                .btn-ghost {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: transparent;
                    color: var(--text);
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 14px;
                    text-decoration: none;
                    border: 1px solid var(--border);
                    transition: border-color 0.15s;
                    margin-left: 12px;
                }
                .btn-ghost:hover { border-color: var(--text); color: var(--text); text-decoration: none; }

                /* PERKS LIST */
                .perks-list { list-style: none; padding: 0; margin: 0 0 24px 0; }
                .perks-list li {
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    padding: 10px 0;
                    border-bottom: 1px solid var(--border);
                    font-size: 14px;
                    color: #CCC;
                }
                .perks-list li:last-child { border-bottom: none; }
                .perk-icon { color: var(--acid); font-size: 16px; margin-top: 1px; flex-shrink: 0; }

                /* STATS ROW */
                .stats-row {
                    display: flex;
                    gap: 1px;
                    background: var(--border);
                    border-radius: 12px;
                    overflow: hidden;
                    margin-top: 20px;
                }
                .stat-item {
                    flex: 1;
                    background: var(--surface);
                    padding: 20px;
                    text-align: center;
                }
                .stat-number {
                    font-size: 28px;
                    font-weight: 700;
                    color: var(--acid);
                    font-family: \'Space Mono\', monospace;
                }
                .stat-label {
                    font-size: 11px;
                    color: var(--muted);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-top: 4px;
                }

                /* RESPONSIVE */
                @media (max-width: 991px) {
                    .radio-hero { grid-template-columns: 1fr; }
                    .radio-logo { font-size: 60px; }
                    .radio-hero-left, .radio-hero-right { padding: 50px 30px; }
                }
            </style>

            <section id="frawo-radio">
                <div class="radio-hero">
                    <!-- LEFT: PLAYER -->
                    <div class="radio-hero-left">
                        <div class="radio-badge">
                            <span class="live-dot"/>
                            Live 24/7
                        </div>
                        <div class="radio-logo">FRAWO<br/><span>FUNK</span></div>
                        <p class="radio-tagline">Broadcasting from the Underground.</p>

                        <!-- PLAYER CARD -->
                        <div class="player-card">
                            <div class="now-playing-label">&#9654; Now Playing</div>
                            <div class="now-playing-meta">
                                <img id="rp-cover" class="cover-art loading" src="/web/image/website/logo.png" alt="Cover Art"/>
                                <div class="track-info">
                                    <div class="track-title" id="rp-title">Verbinde...</div>
                                    <div class="track-artist" id="rp-artist">FraWo Funk</div>
                                    <div class="track-album" id="rp-album"></div>
                                </div>
                                <div class="waveform" id="waveform">
                                    <div class="waveform-bar"/>
                                    <div class="waveform-bar"/>
                                    <div class="waveform-bar"/>
                                    <div class="waveform-bar"/>
                                    <div class="waveform-bar"/>
                                </div>
                            </div>
                            <div class="player-controls">
                                <button class="play-btn" id="rp-play" title="Play/Pause">&#9654;</button>
                                <div class="volume-container">
                                    <span class="volume-icon">&#128266;</span>
                                    <input type="range" id="rp-volume" min="0" max="100" value="80"/>
                                </div>
                            </div>
                            <audio id="rp-audio" preload="none">
                                <source src="https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3" type="audio/mpeg"/>
                            </audio>
                        </div>

                        <!-- VOTING -->
                        <div class="vote-section">
                            <div class="vote-label">Dieser Track?</div>
                            <div class="vote-buttons">
                                <button class="vote-btn love" id="btn-love" onclick="handleVote(\'love\')">
                                    &#10084; Feuer
                                </button>
                                <button class="vote-btn hate" id="btn-hate" onclick="handleVote(\'hate\')">
                                    &#128169; Skip
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- RIGHT: COMMUNITY -->
                    <div class="radio-hero-right">
                        <div class="section-title">&#9733; Community</div>

                        <!-- Show if NOT logged in (Odoo QWeb) -->
                        <t t-if="not request.env.user or request.env.user._is_public()">
                            <div class="community-card">
                                <h3>Werde Teil der Community</h3>
                                <p>Melde dich an und interagiere mit dem Stream: Votings, Requests und exklusive FraWo-News direkt in dein Postfach.</p>
                                <ul class="perks-list">
                                    <li>
                                        <span class="perk-icon">&#9654;</span>
                                        <span>Tracks bewerten &amp; die Playlist beeinflussen</span>
                                    </li>
                                    <li>
                                        <span class="perk-icon">&#9654;</span>
                                        <span>Song-Requests direkt an den DJ</span>
                                    </li>
                                    <li>
                                        <span class="perk-icon">&#9654;</span>
                                        <span>Exklusive Events &amp; Release-Infos</span>
                                    </li>
                                    <li>
                                        <span class="perk-icon">&#9654;</span>
                                        <span>FraWo-Promo: Sets, Remixe, Tickets</span>
                                    </li>
                                </ul>
                                <a href="/web/login?redirect=/radio" class="btn-acid">
                                    Jetzt anmelden
                                </a>
                                <a href="/web/signup" class="btn-ghost">
                                    Account erstellen
                                </a>
                            </div>
                        </t>

                        <!-- Show if logged in -->
                        <t t-if="request.env.user and not request.env.user._is_public()">
                            <div class="community-card">
                                <h3>Willkommen zur&#252;ck, <t t-esc="request.env.user.name.split()[0]"/>! &#128075;</h3>
                                <p>Du bist eingeloggt. Deine Votings beeinflussen direkt die Playlist-Rotation.</p>
                                <ul class="perks-list">
                                    <li>
                                        <span class="perk-icon">&#10003;</span>
                                        <span>Voting aktiviert &amp; z&#228;hlt!</span>
                                    </li>
                                    <li>
                                        <span class="perk-icon">&#10003;</span>
                                        <span>Song-Requests: Bald verf&#252;gbar</span>
                                    </li>
                                </ul>
                                <a href="/odoo/settings" class="btn-ghost">
                                    &#9881; Profil &amp; Einstellungen
                                </a>
                            </div>
                        </t>

                        <!-- STATS -->
                        <div class="stats-row">
                            <div class="stat-item">
                                <div class="stat-number" id="stat-listeners">&#8734;</div>
                                <div class="stat-label">H&#246;rer</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">24/7</div>
                                <div class="stat-label">Live</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number" id="stat-tracks">2000+</div>
                                <div class="stat-label">Tracks</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- TOAST -->
            <div class="vote-toast" id="vote-toast"></div>

            <script>
            //<![CDATA[
            (function() {
                var audio = document.getElementById('rp-audio');
                var playBtn = document.getElementById('rp-play');
                var volumeSlider = document.getElementById('rp-volume');
                var waveform = document.getElementById('waveform');
                var isPlaying = false;
                var currentSongId = null;
                var currentVote = null;
                var isLoggedIn = false;

                // Check login status via Odoo session endpoint
                fetch('/web/session/get_session_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {}})
                }).then(r => r.json()).then(d => {
                    if (d.result && d.result.uid && d.result.uid !== false) {
                        isLoggedIn = true;
                    }
                });

                // Play/Pause
                playBtn.addEventListener('click', function() {
                    if (isPlaying) {
                        audio.pause();
                        playBtn.innerHTML = '&#9654;';
                        waveform.classList.remove('active');
                        isPlaying = false;
                    } else {
                        audio.load();
                        audio.play().then(() => {
                            playBtn.innerHTML = '&#9646;&#9646;';
                            waveform.classList.add('active');
                            isPlaying = true;
                        }).catch(e => console.log('Playback error:', e));
                    }
                });

                // Volume
                volumeSlider.addEventListener('input', function() {
                    audio.volume = this.value / 100;
                });
                audio.volume = 0.8;

                // Now Playing API
                function updateNowPlaying() {
                    fetch('https://funk.frawo-tech.de/api/nowplaying/1')
                        .then(r => r.json())
                        .then(function(d) {
                            var np = d.now_playing;
                            if (!np) return;
                            var song = np.song;
                            var newId = song.id;

                            // Reset vote on new song
                            if (newId !== currentSongId) {
                                currentSongId = newId;
                                currentVote = null;
                                document.getElementById('btn-love').className = 'vote-btn love';
                                document.getElementById('btn-hate').className = 'vote-btn hate';
                            }

                            document.getElementById('rp-title').textContent = song.title || 'Unknown Track';
                            document.getElementById('rp-artist').textContent = song.artist || '';
                            document.getElementById('rp-album').textContent = song.album ? '&#11835; ' + song.album : '';

                            var cover = document.getElementById('rp-cover');
                            if (song.art) {
                                cover.src = song.art;
                                cover.classList.remove('loading');
                            }

                            // Listeners
                            if (d.listeners) {
                                var el = document.getElementById('stat-listeners');
                                if (el) el.textContent = d.listeners.current || 0;
                            }
                        })
                        .catch(function(e) { console.log('Now playing error:', e); });
                }

                updateNowPlaying();
                setInterval(updateNowPlaying, 10000);

                // Toast notification
                function showToast(msg) {
                    var toast = document.getElementById('vote-toast');
                    toast.textContent = msg;
                    toast.classList.add('show');
                    setTimeout(function() { toast.classList.remove('show'); }, 3000);
                }

                // Voting
                window.handleVote = function(type) {
                    if (!isLoggedIn) {
                        // Save current URL and redirect to Odoo login
                        window.location.href = '/web/login?redirect=/radio';
                        return;
                    }
                    if (currentVote === type) {
                        showToast('Du hast bereits abgestimmt! &#128521;');
                        return;
                    }
                    currentVote = type;

                    // Optimistic UI update
                    document.getElementById('btn-love').className = 'vote-btn love' + (type === 'love' ? ' voted-love' : '');
                    document.getElementById('btn-hate').className = 'vote-btn hate' + (type === 'hate' ? ' voted-hate' : '');

                    showToast(type === 'love' ? '&#10084; Feuer! Kommt &#246;fter!' : '&#128169; Skip registriert!');

                    // Send to our backend (Odoo controller or Worker)
                    fetch('/radio/vote', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({
                            jsonrpc: '2.0',
                            method: 'call',
                            params: {
                                song_id: currentSongId,
                                vote_type: type
                            }
                        })
                    }).then(r => r.json()).then(d => {
                        console.log('Vote response:', d);
                    }).catch(e => console.log('Vote error:', e));
                };
            })();
            //]]>
            </script>
        </div>
    </t>
</t>'''

# Update existing view
existing_view = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.ui.view', 'search',
    [[('key', '=', 'website.frawo_radio_page')]]
)

if existing_view:
    view_id = existing_view[0]
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [view_id, {'arch': page_html}])
    print(f"Updated existing view {view_id}")
else:
    view_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
        'name': 'FraWo Funk Radio Page',
        'type': 'qweb',
        'key': 'website.frawo_radio_page',
        'arch': page_html,
    }])
    print(f"Created new view {view_id}")

# Ensure the page exists and is published
existing_page = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'search',
    [[('url', '=', '/radio')]]
)

if existing_page:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'write',
        [existing_page[0], {'view_id': view_id, 'is_published': True}])
    print(f"Updated page /radio - published")
else:
    page_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'create', [{
        'name': 'FraWo Funk',
        'url': '/radio',
        'view_id': view_id,
        'is_published': True,
        'website_published': True,
    }])
    print(f"Created page /radio (ID: {page_id}) - published")

print("\n✓ FraWo Funk Radio page deployed!")
print("  URL: http://10.1.0.112:8069/radio")
print("  - Live now-playing from AzuraCast API")
print("  - Voting (Herz/Kackhaufen) with login check")
print("  - Community register/login panel")
print("  - Native Odoo user detection (QWeb)")
