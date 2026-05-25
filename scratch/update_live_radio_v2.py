import xmlrpc.client
import os
import base64
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Read Logo
logo_path = Path("brand_assets/frawo_funk_logo.png")
logo_b64 = ""
if logo_path.exists():
    with open(logo_path, "rb") as f:
         logo_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

live_html = """<?xml version="1.0"?>
<t name="FraWo Funk Premium" t-name="website.frawo_radio_page">
    <t t-call="website.layout">
        <!-- DISABLE STANDARD ODOO HEADER AND FOOTER -->
        <t t-set="no_header" t-value="True"/>
        <t t-set="no_footer" t-value="True"/>
        
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800;900&amp;display=swap" rel="stylesheet"/>
        
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                background-color: #050505;
            }
            .frawo-radio-container {
                font-family: 'Outfit', sans-serif;
                background-color: #050505;
                background: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #050505 100%);
                color: #fff;
                min-height: 100vh;
                position: relative;
                overflow-x: hidden;
                display: flex;
                flex-direction: column;
            }
            .frawo-radio-overlay {
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(135deg, rgba(5,5,5,0.95) 0%, rgba(139,92,246,0.15) 50%, rgba(16,185,129,0.1) 100%);
                z-index: 0;
                pointer-events: none;
            }
            .frawo-content {
                position: relative;
                z-index: 10;
                display: flex;
                flex-direction: column;
                flex-grow: 1;
            }
            /* HEADER LOGO */
            .radio-header {
                padding: 20px 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .radio-logo {
                height: 60px;
                width: auto;
            }
            .back-to-main {
                color: #8B5CF6;
                text-decoration: none;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 14px;
                transition: color 0.3s;
            }
            .back-to-main:hover {
                color: #10B981;
            }
            
            .marquee-container {
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                border-bottom: 1px solid rgba(139,92,246,0.3);
                padding: 10px 0;
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(10px);
            }
            .marquee-text {
                display: inline-block;
                padding-left: 100%;
                animation: marquee 20s linear infinite;
                font-weight: 800;
                letter-spacing: 4px;
                color: #10B981;
                text-transform: uppercase;
                font-size: 14px;
            }
            @keyframes marquee {
                0% { transform: translate(0, 0); }
                100% { transform: translate(-100%, 0); }
            }
            
            .player-grid {
                display: grid;
                grid-template-columns: 1fr 400px;
                gap: 40px;
                padding: 40px;
                flex-grow: 1;
            }
            @media(max-width: 991px) {
                .player-grid { grid-template-columns: 1fr; }
            }
            
            .title-section h1 {
                font-size: clamp(3rem, 6vw, 8rem);
                font-weight: 900;
                line-height: 0.9;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: -2px;
            }
            .title-funk {
                color: transparent;
                -webkit-text-stroke: 2px #10B981;
                background: linear-gradient(90deg, #10B981, #8B5CF6);
                -webkit-background-clip: text;
                animation: pulse-glow 4s ease-in-out infinite alternate;
            }
            @keyframes pulse-glow {
                0% { text-shadow: 0 0 20px rgba(16,185,129,0.1); }
                100% { text-shadow: 0 0 40px rgba(139,92,246,0.4); }
            }
            
            /* GLASSMORPHISM PANELS */
            .glass-panel {
                background: rgba(20, 20, 20, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            }
            .glass-panel:hover {
                transform: translateY(-5px);
                box-shadow: 0 30px 60px -12px rgba(139,92,246, 0.15);
                border-color: rgba(139,92,246, 0.2);
            }
            
            /* PLAYER BUTTON */
            .play-btn {
                width: 90px;
                height: 90px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10B981, #059669);
                border: none;
                color: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 10px 25px rgba(16,185,129,0.4);
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                outline: none;
            }
            .play-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 15px 35px rgba(16,185,129,0.6);
            }
            .play-btn svg {
                width: 35px; height: 35px; fill: currentColor;
                margin-left: 5px;
            }
            .play-btn.playing svg { margin-left: 0; }
            
            /* VISUALIZER */
            .visualizer-container {
                display: flex;
                align-items: flex-end;
                height: 120px;
                gap: 4px;
                margin-top: 40px;
                border-bottom: 2px solid rgba(255,255,255,0.1);
            }
            .bar {
                flex: 1;
                background: #4c1d95;
                border-radius: 2px 2px 0 0;
                min-height: 4px;
                transition: height 0.05s ease;
            }
            
            /* NOW PLAYING */
            .now-playing-container {
                background: rgba(0,0,0,0.4);
                border-left: 4px solid #8B5CF6;
                padding: 15px 20px;
                margin-top: 30px;
                border-radius: 0 8px 8px 0;
            }
            .np-label {
                font-size: 11px;
                color: #8B5CF6;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 800;
                margin-bottom: 5px;
            }
            .np-title {
                font-size: 24px;
                font-weight: 700;
                color: #fff;
                margin: 0;
            }
            .np-artist {
                font-size: 16px;
                color: #10B981;
                font-weight: 500;
            }
            
            /* MISC */
            .status-dot {
                width: 10px; height: 10px;
                background-color: #ef4444;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
                box-shadow: 0 0 10px #ef4444;
            }
            .status-dot.active {
                background-color: #10B981;
                box-shadow: 0 0 15px #10B981;
                animation: blink 2s infinite;
            }
            @keyframes blink {
                0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; }
            }
            
            /* COMMUNITY BTN */
            .btn-community {
                background: linear-gradient(135deg, #8B5CF6, #6d28d9);
                color: #fff;
                padding: 12px 20px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 14px;
                display: inline-block;
                transition: all 0.2s;
                box-shadow: 0 4px 15px rgba(139,92,246,0.4);
                border: none;
                width: 100%;
                text-align: center;
            }
            .btn-community:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(139,92,246,0.6);
                color: #fff;
            }
            
            /* CHAT (MOCK) */
            .chat-box {
                background: rgba(0,0,0,0.3);
                border-radius: 8px;
                height: 300px;
                padding: 15px;
                margin-top: 15px;
                border: 1px solid rgba(255,255,255,0.05);
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
            }
            .chat-message {
                margin-bottom: 10px;
                font-size: 13px;
                line-height: 1.4;
            }
            .chat-user {
                color: #10B981;
                font-weight: bold;
                margin-right: 5px;
            }
        </style>

        <div class="frawo-radio-container">
            <div class="frawo-radio-overlay"></div>
            
            <div class="frawo-content">
                <!-- HEADER -->
                <div class="radio-header">
                    <img src=\"""" + logo_b64 + """\" alt="FraWo Funk" class="radio-logo" t-if="\'""" + logo_b64 + """\' != ''"/>
                    <div t-else="" style="font-weight: 900; font-size: 24px; letter-spacing: 2px;">FRAWO <span style="color:#10B981">FUNK</span></div>
                    <a href="/" class="back-to-main">← Back to FraWo</a>
                </div>
                
                <div class="marquee-container">
                    <div class="marquee-text">
                        +++ FRAWO FUNK +++ LIVE BROADCAST +++ UNDERGROUND ELECTRONIC +++ THE MACHINE IS RUNNING +++
                    </div>
                </div>
                
                <div class="player-grid">
                    <div class="title-section d-flex flex-column justify-content-center">
                        <h1 class="title-frawo">THE</h1>
                        <h1 class="title-funk">UNDERGROUND</h1>
                        
                        <div class="now-playing-container">
                            <div class="np-label">Now Playing</div>
                            <div class="np-title" id="np-title">Loading Stream...</div>
                            <div class="np-artist" id="np-artist">FraWo Auto-DJ</div>
                        </div>
                        
                        <div class="mt-5 d-flex align-items-center gap-4">
                            <button id="main-play-btn" class="play-btn">
                                <svg id="icon-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                                <svg id="icon-pause" viewBox="0 0 24 24" style="display:none;"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                            </button>
                            <div>
                                <div class="d-flex align-items-center mb-1">
                                    <span id="live-indicator" class="status-dot"></span>
                                    <span style="text-transform: uppercase; font-weight: 800; color: #fff; letter-spacing: 2px;" id="stream-status">Offline</span>
                                </div>
                                <div style="font-size: 13px; color: #888;">320kbps MP3 Stream</div>
                            </div>
                        </div>
                        
                        <!-- Web Audio API Live Visualizer -->
                        <div class="visualizer-container" id="visualizer">
                            <!-- Bars generated by JS -->
                        </div>
                    </div>
                    
                    <div class="sidebar-section">
                        <!-- Community / Login Panel -->
                        <div class="glass-panel mb-4">
                            <h3 style="font-weight: 900; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px; color: #10B981;">The Community</h3>
                            
                            <t t-if="request.env.user.id == request.env.ref('base.public_user').id">
                                <!-- User is NOT logged in -->
                                <p style="color: #ccc; font-size: 14px; margin-bottom: 25px; line-height: 1.6;">
                                    Du bist nicht eingeloggt. Werde Teil des Undergrounds, um im Live-Chat zu interagieren.
                                </p>
                                <a href="/web/login?redirect=/frawo-funk" class="btn-community mb-2">VIP Login</a>
                                <div class="text-center mt-3">
                                    <a href="/web/signup?redirect=/frawo-funk" style="color: #888; font-size: 12px; text-decoration: none;">Noch kein Account? Registrieren</a>
                                </div>
                            </t>
                            <t t-else="">
                                <!-- User IS logged in -->
                                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
                                    <img t-attf-src="/web/image/res.users/{{request.env.user.id}}/avatar_128" style="width: 45px; height: 45px; border-radius: 50%; border: 2px solid #8B5CF6;"/>
                                    <div>
                                        <div style="font-size: 11px; color: #8B5CF6; text-transform: uppercase; font-weight: bold;">VIP Access</div>
                                        <div style="font-weight: bold; color: #fff; font-size: 16px;"><t t-esc="request.env.user.name"/></div>
                                    </div>
                                </div>
                                
                                <div class="chat-box">
                                    <div class="chat-message"><span class="chat-user">TheMachine:</span> Welcome to the stream.</div>
                                    <div class="chat-message"><span class="chat-user">TheMachine:</span> Der Chat ist derzeit im Read-Only Modus (Beta).</div>
                                    <input type="text" placeholder="Nachricht eingeben..." disabled="disabled" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #fff; margin-top: 15px;"/>
                                </div>
                            </t>
                        </div>
                    </div>
                </div>
            </div>
            
            <audio id="audio-stream" crossorigin="anonymous" src="https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3"></audio>
        </div>
        
        <script>
            // <![CDATA[
            document.addEventListener('DOMContentLoaded', function() {
                const audio = document.getElementById('audio-stream');
                const playBtn = document.getElementById('main-play-btn');
                const iconPlay = document.getElementById('icon-play');
                const iconPause = document.getElementById('icon-pause');
                const liveIndicator = document.getElementById('live-indicator');
                const streamStatus = document.getElementById('stream-status');
                const visualizer = document.getElementById('visualizer');
                
                const npTitle = document.getElementById('np-title');
                const npArtist = document.getElementById('np-artist');
                
                // Fetch AzuraCast Now Playing Data
                function fetchNowPlaying() {
                    fetch('https://funk.frawo-tech.de/api/nowplaying/1')
                        .then(response => response.json())
                        .then(data => {
                            if(data && data.now_playing && data.now_playing.song) {
                                npTitle.innerText = data.now_playing.song.title || 'Unknown Title';
                                npArtist.innerText = data.now_playing.song.artist || 'Unknown Artist';
                            }
                        })
                        .catch(err => console.log('NowPlaying API Error:', err));
                }
                
                // Fetch immediately and then every 15 seconds
                fetchNowPlaying();
                setInterval(fetchNowPlaying, 15000);
                
                // Web Audio API Elements
                let audioCtx = null;
                let analyser = null;
                let source = null;
                let dataArray = null;
                let bufferLength = null;
                let fallbackInterval = null;
                
                // Create visualizer bars
                const numBars = 45;
                for(let i=0; i<numBars; i++) {
                    const bar = document.createElement('div');
                    bar.className = 'bar';
                    visualizer.appendChild(bar);
                }
                const bars = document.querySelectorAll('.bar');
                
                let isPlaying = false;
                let animFrame;
                let useFallback = false;
                
                function initAudioContext() {
                    if (!audioCtx) {
                        try {
                            const AudioContext = window.AudioContext || window.webkitAudioContext;
                            audioCtx = new AudioContext();
                            analyser = audioCtx.createAnalyser();
                            
                            source = audioCtx.createMediaElementSource(audio);
                            source.connect(analyser);
                            analyser.connect(audioCtx.destination);
                            
                            analyser.fftSize = 128; // 64 bins
                            bufferLength = analyser.frequencyBinCount;
                            dataArray = new Uint8Array(bufferLength);
                        } catch (e) {
                            console.error("Web Audio API blocked by CORS. Using fallback visualizer.", e);
                            useFallback = true;
                        }
                    }
                    if(audioCtx && audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                }
                
                function updateVisualizer() {
                    if(isPlaying && !useFallback && analyser) {
                        analyser.getByteFrequencyData(dataArray);
                        
                        let hasData = false;
                        bars.forEach((bar, index) => {
                            if(index < bufferLength) {
                                let val = dataArray[index];
                                if(val > 0) hasData = true;
                                let percent = Math.max(5, (val / 255) * 100);
                                bar.style.height = percent + '%';
                                
                                if(percent > 85) bar.style.background = '#10B981';
                                else if(percent > 45) bar.style.background = '#8B5CF6';
                                else bar.style.background = '#4c1d95';
                            }
                        });
                        
                        // If all zeros, maybe CORS blocked after init. Switch to fallback.
                        if(!hasData && audio.currentTime > 2) {
                            useFallback = true;
                        } else {
                            animFrame = requestAnimationFrame(updateVisualizer);
                        }
                    }
                    
                    if(isPlaying && useFallback) {
                        // Fallback Fake Visualizer for CORS restricted environments
                        bars.forEach((bar) => {
                            let randomPercent = Math.max(5, Math.random() * 80);
                            bar.style.height = randomPercent + '%';
                            if(randomPercent > 70) bar.style.background = '#10B981';
                            else if(randomPercent > 40) bar.style.background = '#8B5CF6';
                            else bar.style.background = '#4c1d95';
                        });
                        fallbackInterval = setTimeout(updateVisualizer, 100); // 10fps fake anim
                    }
                }
                
                function stopVisualizer() {
                    cancelAnimationFrame(animFrame);
                    clearTimeout(fallbackInterval);
                    bars.forEach(bar => {
                        bar.style.height = '4px';
                        bar.style.background = '#4c1d95';
                    });
                }

                playBtn.addEventListener('click', function() {
                    if(isPlaying) {
                        audio.pause();
                        iconPlay.style.display = 'block';
                        iconPause.style.display = 'none';
                        playBtn.classList.remove('playing');
                        liveIndicator.classList.remove('active');
                        streamStatus.innerText = 'OFFLINE';
                        isPlaying = false;
                        stopVisualizer();
                    } else {
                        initAudioContext();
                        
                        audio.play().then(() => {
                            iconPlay.style.display = 'none';
                            iconPause.style.display = 'block';
                            playBtn.classList.add('playing');
                            liveIndicator.classList.add('active');
                            streamStatus.innerText = 'ON AIR';
                            isPlaying = true;
                            updateVisualizer();
                        }).catch(e => {
                            console.error("Audio play failed:", e);
                            streamStatus.innerText = 'PLAY ERROR';
                            stopVisualizer();
                        });
                    }
                });
            });
            // ]]>
        </script>
    </t>
</t>"""

existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website.frawo_radio_page')]])
if existing_view:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0], {'arch': live_html}])
    print("SUCCESS: Updated NTS Style Radio page with AzuraCast NowPlaying API integration.")
else:
    print("ERROR: View 'website.frawo_radio_page' not found!")
