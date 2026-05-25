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

# Re-read background image
image_path = list(Path('.').glob('frawo_funk_bg_*.png'))
bg_image = ""
if image_path:
    with open(image_path[0], "rb") as f:
         b64 = base64.b64encode(f.read()).decode("utf-8")
         bg_image = "data:image/png;base64," + b64

live_html = """<?xml version="1.0"?>
<t name="FraWo Funk Premium" t-name="website.frawo_radio_page">
    <t t-call="website.layout">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800;900&amp;display=swap" rel="stylesheet"/>
        
        <style>
            .frawo-radio-container {
                font-family: 'Outfit', sans-serif;
                background-color: #050505;
                background-image: url('""" + bg_image + """');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: #fff;
                min-height: 90vh;
                position: relative;
                overflow: hidden;
            }
            .frawo-radio-overlay {
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(135deg, rgba(5,5,5,0.9) 0%, rgba(139,92,246,0.1) 50%, rgba(16,185,129,0.1) 100%);
                z-index: 0;
            }
            .frawo-content {
                position: relative;
                z-index: 10;
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            .marquee-container {
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                border-top: 1px solid rgba(255,255,255,0.1);
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
                color: #8B5CF6;
                text-transform: uppercase;
                font-size: 14px;
            }
            @keyframes marquee {
                0% { transform: translate(0, 0); }
                100% { transform: translate(-100%, 0); }
            }
            .player-grid {
                display: grid;
                grid-template-columns: 1fr 450px;
                gap: 40px;
                padding: 60px 40px;
                flex-grow: 1;
            }
            @media(max-width: 991px) {
                .player-grid { grid-template-columns: 1fr; }
            }
            .title-section h1 {
                font-size: clamp(4rem, 8vw, 10rem);
                font-weight: 900;
                line-height: 0.85;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: -2px;
                text-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .title-funk {
                color: transparent;
                -webkit-text-stroke: 2px #10B981;
                background: linear-gradient(90deg, #10B981, #8B5CF6);
                -webkit-background-clip: text;
                animation: pulse-glow 4s ease-in-out infinite alternate;
            }
            @keyframes pulse-glow {
                0% { text-shadow: 0 0 20px rgba(16,185,129,0.2); }
                100% { text-shadow: 0 0 40px rgba(139,92,246,0.6); }
            }
            .glass-panel {
                background: rgba(20, 20, 20, 0.4);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .glass-panel:hover {
                transform: translateY(-5px);
                box-shadow: 0 30px 60px -12px rgba(139,92,246, 0.2);
                border-color: rgba(139,92,246, 0.3);
            }
            .play-btn {
                width: 100px;
                height: 100px;
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
                width: 40px; height: 40px; fill: currentColor;
                margin-left: 5px;
            }
            .play-btn.playing svg { margin-left: 0; }
            
            .visualizer-container {
                display: flex;
                align-items: flex-end;
                height: 100px;
                gap: 5px;
                margin-top: 30px;
                border-bottom: 2px solid rgba(255,255,255,0.1);
            }
            .bar {
                flex: 1;
                background: #8B5CF6;
                border-radius: 2px 2px 0 0;
                min-height: 4px;
                /* No CSS transition here, JS handles the rapid updates */
            }
            .schedule-item {
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding: 20px 0;
                transition: padding-left 0.3s ease;
            }
            .schedule-item:hover {
                padding-left: 10px;
                border-color: #10B981;
            }
            .status-dot {
                width: 12px; height: 12px;
                background-color: #ef4444;
                border-radius: 50%;
                display: inline-block;
                margin-right: 10px;
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
            .btn-community {
                background: linear-gradient(135deg, #10B981, #059669);
                color: #fff;
                padding: 12px 20px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 14px;
                display: inline-block;
                transition: all 0.2s;
                box-shadow: 0 4px 15px rgba(16,185,129,0.4);
                border: none;
            }
            .btn-community:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(16,185,129,0.6);
                color: #fff;
            }
        </style>

        <div class="frawo-radio-container">
            <div class="frawo-radio-overlay"></div>
            
            <div class="frawo-content">
                <div class="marquee-container">
                    <div class="marquee-text">
                        +++ FRAWO FUNK +++ LIVE BROADCAST +++ UNDERGROUND ELECTRONIC +++ JOIN THE COMMUNITY +++ FRAWO FUNK +++
                    </div>
                </div>
                
                <div class="player-grid">
                    <div class="title-section d-flex flex-column justify-content-center">
                        <h1 class="title-frawo">FraWo</h1>
                        <h1 class="title-funk">Funk</h1>
                        <p class="mt-4" style="font-size: 1.2rem; color: #aaa; max-width: 500px; line-height: 1.6;">
                            Tauchen Sie ein in die klangliche Architektur von FraWo. Elektronische Beats, tiefe Bässe und kompromisslose Rotation direkt aus unserem Studio.
                        </p>
                        
                        <div class="mt-5 d-flex align-items-center gap-4">
                            <button id="main-play-btn" class="play-btn">
                                <svg id="icon-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                                <svg id="icon-pause" viewBox="0 0 24 24" style="display:none;"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                            </button>
                            <div>
                                <div class="d-flex align-items-center mb-1">
                                    <span id="live-indicator" class="status-dot"></span>
                                    <span style="text-transform: uppercase; font-weight: 800; color: #fff; letter-spacing: 2px;">Offline</span>
                                </div>
                                <div id="track-name" style="font-size: 1.5rem; font-weight: 500; color: #10B981;">Bereit zum Streamen</div>
                            </div>
                        </div>
                        
                        <!-- Web Audio API Live Visualizer -->
                        <div class="visualizer-container" id="visualizer">
                            <!-- Bars generated by JS -->
                        </div>
                    </div>
                    
                    <div class="schedule-section">
                        <!-- Community / Login Panel -->
                        <div class="glass-panel mb-4" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3);">
                            <h3 style="font-weight: 900; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px; border-bottom: 2px solid #10B981; padding-bottom: 15px; display: inline-block;">FraWo Community</h3>
                            <p style="color: #ccc; font-size: 14px; margin-bottom: 25px; line-height: 1.6;">
                                Unterstütze den Underground. Melde dich an, um bald Features wie Live-Chat, Track-Voting und direkten Draht ins Studio freizuschalten.
                            </p>
                            
                            <t t-if="request.env.user.id == request.env.ref('base.public_user').id">
                                <!-- User is NOT logged in -->
                                <a href="/web/signup" class="btn-community w-100 text-center mb-2">Join the Underground</a>
                                <div class="text-center mt-3">
                                    <a href="/web/login" style="color: #8B5CF6; font-size: 13px; font-weight: bold; text-decoration: none;">Bereits Mitglied? Login</a>
                                </div>
                            </t>
                            <t t-else="">
                                <!-- User IS logged in -->
                                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                                    <img t-attf-src="/web/image/res.users/{{request.env.user.id}}/avatar_128" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #10B981;"/>
                                    <div>
                                        <div style="font-size: 12px; color: #aaa; text-transform: uppercase;">Eingeloggt als</div>
                                        <div style="font-weight: bold; color: #fff; font-size: 16px;"><t t-esc="request.env.user.name"/></div>
                                    </div>
                                </div>
                                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 13px; color: #10B981; border: 1px dashed #10B981;">
                                    🚀 VIP Access gewährt. Live-Chat &amp; Community-Features in Kürze verfügbar!
                                </div>
                            </t>
                        </div>
                        
                        <div class="glass-panel">
                            <h3 style="font-weight: 900; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; border-bottom: 2px solid #8B5CF6; padding-bottom: 15px; display: inline-block;">Schedule</h3>
                            
                            <div class="schedule-item">
                                <div style="color: #8B5CF6; font-weight: 800; font-size: 14px; margin-bottom: 5px;">24 / 7</div>
                                <div style="font-weight: 800; font-size: 22px; text-transform: uppercase;">The Machine</div>
                                <div style="color: #888; font-size: 14px; margin-top: 5px;">Automatisierte FraWo-Selection. Kein Gerede, nur Beats.</div>
                            </div>
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
                const trackName = document.getElementById('track-name');
                const visualizer = document.getElementById('visualizer');
                
                // Web Audio API Elements
                let audioCtx = null;
                let analyser = null;
                let source = null;
                let dataArray = null;
                let bufferLength = null;
                
                // Create visualizer bars
                const numBars = 40;
                for(let i=0; i<numBars; i++) {
                    const bar = document.createElement('div');
                    bar.className = 'bar';
                    visualizer.appendChild(bar);
                }
                const bars = document.querySelectorAll('.bar');
                
                let isPlaying = false;
                let animFrame;
                
                function initAudioContext() {
                    if (!audioCtx) {
                        const AudioContext = window.AudioContext || window.webkitAudioContext;
                        audioCtx = new AudioContext();
                        analyser = audioCtx.createAnalyser();
                        
                        // We must use crossorigin="anonymous" on the audio element!
                        source = audioCtx.createMediaElementSource(audio);
                        source.connect(analyser);
                        analyser.connect(audioCtx.destination);
                        
                        analyser.fftSize = 128; // 64 frequency bins
                        bufferLength = analyser.frequencyBinCount;
                        dataArray = new Uint8Array(bufferLength);
                    }
                    if(audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                }
                
                function updateVisualizer() {
                    if(isPlaying && analyser) {
                        analyser.getByteFrequencyData(dataArray);
                        
                        // we only map the first `numBars` bins, since higher frequencies are often empty
                        bars.forEach((bar, index) => {
                            if(index < bufferLength) {
                                let val = dataArray[index]; // 0 to 255
                                // Map to height
                                let percent = Math.max(5, (val / 255) * 100);
                                bar.style.height = percent + '%';
                                
                                // Dynamic color based on amplitude
                                if(percent > 80) {
                                    bar.style.background = '#10B981';
                                } else if(percent > 40) {
                                    bar.style.background = '#8B5CF6';
                                } else {
                                    bar.style.background = '#4c1d95'; // Darker violet
                                }
                            }
                        });
                        animFrame = requestAnimationFrame(updateVisualizer);
                    }
                }
                
                function stopVisualizer() {
                    cancelAnimationFrame(animFrame);
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
                        liveIndicator.nextElementSibling.innerText = 'OFFLINE';
                        trackName.innerText = 'Pausiert';
                        isPlaying = false;
                        stopVisualizer();
                    } else {
                        // init audio context ON click to bypass browser restrictions
                        initAudioContext();
                        
                        // Attempt to grab stream metadata if possible (Icecast title)
                        trackName.innerText = 'Live Stream aktiv';
                        
                        audio.play().then(() => {
                            iconPlay.style.display = 'none';
                            iconPause.style.display = 'block';
                            playBtn.classList.add('playing');
                            liveIndicator.classList.add('active');
                            liveIndicator.nextElementSibling.innerText = 'ON AIR';
                            isPlaying = true;
                            updateVisualizer();
                        }).catch(e => {
                            console.error("Audio play failed (CORS or Autoplay restriction):", e);
                            trackName.innerText = 'Fehler beim Stream / CORS';
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
    print("Updated premium Radio page with Live Visualizer and Community panel.")
else:
    print("View not found!")
