import xmlrpc.client
import os
import base64
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
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
        
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&amp;display=swap" rel="stylesheet"/>
        
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                background-color: #030303;
                overflow: hidden; /* Prevent scrolling for app feel */
            }
            .frawo-app {
                font-family: 'Outfit', sans-serif;
                color: #fff;
                height: 100vh;
                width: 100vw;
                position: relative;
                display: flex;
                flex-direction: column;
            }
            /* DYNAMIC BACKGROUND */
            .bg-dynamic {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background: radial-gradient(circle at 50% 50%, rgba(139,92,246,0.15) 0%, rgba(16,185,129,0.05) 40%, rgba(3,3,3,1) 80%);
                z-index: 1;
                transition: transform 0.1s ease-out, background 0.1s ease-out;
            }
            /* CANVAS VISUALIZER */
            #canvas-visualizer {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 60%;
                z-index: 2;
                opacity: 0.8;
                pointer-events: none;
            }
            /* OVERSIZED TYPOGRAPHY PARALLAX */
            .bg-text {
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                font-size: 25vw;
                font-weight: 900;
                color: transparent;
                -webkit-text-stroke: 1px rgba(255,255,255,0.03);
                z-index: 3;
                white-space: nowrap;
                pointer-events: none;
                user-select: none;
            }
            
            /* TOP HEADER */
            .top-bar {
                position: relative;
                z-index: 10;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 30px 50px;
            }
            .logo-img {
                height: 60px;
                filter: drop-shadow(0 0 10px rgba(16,185,129,0.5));
            }
            .nav-link {
                color: #8B5CF6;
                text-decoration: none;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 2px;
                transition: color 0.3s;
                font-size: 14px;
            }
            .nav-link:hover {
                color: #10B981;
            }

            /* MAIN LAYOUT */
            .main-content {
                position: relative;
                z-index: 10;
                display: flex;
                flex: 1;
                padding: 0 50px 50px 50px;
                align-items: center;
                justify-content: space-between;
            }
            
            /* PLAYER CONTROLS (LEFT) */
            .player-container {
                display: flex;
                flex-direction: column;
                max-width: 600px;
            }
            .station-name {
                font-size: 5rem;
                font-weight: 900;
                line-height: 0.9;
                margin: 0 0 20px 0;
                background: linear-gradient(90deg, #10B981, #8B5CF6);
                -webkit-background-clip: text;
                color: transparent;
                text-transform: uppercase;
                letter-spacing: -2px;
            }
            .now-playing {
                margin-top: 10px;
                background: rgba(0,0,0,0.4);
                backdrop-filter: blur(10px);
                border-left: 3px solid #10B981;
                padding: 15px 25px;
                border-radius: 0 8px 8px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .np-label {
                font-size: 11px;
                color: #8B5CF6;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .np-title {
                font-size: 28px;
                font-weight: 800;
                color: #fff;
                margin: 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .np-artist {
                font-size: 18px;
                color: #10B981;
                font-weight: 400;
            }
            
            .controls-wrapper {
                display: flex;
                align-items: center;
                gap: 30px;
                margin-top: 50px;
            }
            
            .play-ring {
                position: relative;
                width: 120px;
                height: 120px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .play-btn {
                position: relative;
                z-index: 2;
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
                box-shadow: 0 10px 30px rgba(16,185,129,0.5);
                transition: transform 0.1s;
                outline: none;
            }
            .play-btn:hover {
                background: linear-gradient(135deg, #34d399, #10B981);
            }
            .play-btn svg {
                width: 40px; height: 40px; fill: currentColor;
                margin-left: 6px;
            }
            .play-btn.playing svg { margin-left: 0; }
            
            /* AUDIO REACTIVE RIPPLES */
            .ripple {
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                width: 90px; height: 90px;
                border-radius: 50%;
                background: rgba(16,185,129,0.4);
                z-index: 1;
                opacity: 0;
                pointer-events: none;
                transition: width 0.1s ease-out, height 0.1s ease-out, opacity 0.1s ease-out;
            }

            .status-indicator {
                display: flex;
                flex-direction: column;
            }
            .status-badge {
                display: inline-flex;
                align-items: center;
                padding: 6px 12px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: #888;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .status-badge.live {
                color: #10B981;
                border-color: rgba(16,185,129,0.3);
                background: rgba(16,185,129,0.05);
            }
            .status-dot {
                width: 8px; height: 8px;
                background-color: #ef4444;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-badge.live .status-dot {
                background-color: #10B981;
                box-shadow: 0 0 10px #10B981;
            }
            
            /* SIDEBAR (RIGHT) */
            .sidebar {
                width: 380px;
                height: 100%;
                background: rgba(10, 10, 10, 0.6);
                backdrop-filter: blur(20px);
                border-left: 1px solid rgba(255,255,255,0.05);
                padding: 40px 30px;
                display: flex;
                flex-direction: column;
            }
            .sidebar-title {
                font-size: 18px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #fff;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
            }
            .sidebar-title::before {
                content: '';
                display: inline-block;
                width: 15px; height: 3px;
                background: #8B5CF6;
                margin-right: 10px;
            }
            
            /* CHAT BOX */
            .chat-container {
                flex: 1;
                background: rgba(0,0,0,0.4);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.05);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .chat-msg {
                font-size: 13px;
                line-height: 1.5;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .msg-user {
                color: #10B981;
                font-weight: 700;
                margin-right: 5px;
            }
            .msg-sys {
                color: #8B5CF6;
                font-style: italic;
            }
            
            .chat-input-area {
                padding: 15px;
                background: rgba(20,20,20,0.8);
                border-top: 1px solid rgba(255,255,255,0.05);
            }
            .chat-input {
                width: 100%;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                color: #fff;
                padding: 12px 15px;
                border-radius: 8px;
                font-family: 'Outfit', sans-serif;
                font-size: 13px;
                outline: none;
                transition: border-color 0.3s;
            }
            .chat-input:focus {
                border-color: #8B5CF6;
            }
            
            /* LOGIN STATES */
            .auth-panel {
                margin-top: 20px;
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 20px;
            }
            .btn-action {
                display: block;
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                text-decoration: none;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 13px;
                transition: all 0.3s;
            }
            .btn-primary {
                background: linear-gradient(135deg, #10B981, #059669);
                color: #fff;
                border: none;
                box-shadow: 0 4px 15px rgba(16,185,129,0.3);
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(16,185,129,0.5);
                color: #fff;
            }
            .btn-outline {
                background: transparent;
                color: #fff;
                border: 1px solid #8B5CF6;
            }
            .btn-outline:hover {
                background: rgba(139,92,246,0.1);
                color: #fff;
            }
            
            .user-profile {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .user-avatar {
                width: 45px; height: 45px;
                border-radius: 50%;
                border: 2px solid #8B5CF6;
                padding: 2px;
            }
            
        </style>

        <div class="frawo-app" id="app-container">
            <!-- DYNAMIC BACKGROUND -->
            <div class="bg-dynamic" id="bg-dynamic"></div>
            
            <div class="bg-text">FRAWO FUNK</div>
            
            <!-- CANVAS VISUALIZER -->
            <canvas id="canvas-visualizer"></canvas>
            
            <!-- HEADER -->
            <div class="top-bar">
                <img src=\"""" + logo_b64 + """\" alt="FraWo Funk" class="logo-img" t-if="\'""" + logo_b64 + """\' != ''"/>
                <div t-else="" style="font-weight: 900; font-size: 28px; letter-spacing: 2px; z-index: 10;">FRAWO <span style="color:#10B981">FUNK</span></div>
                <a href="/" class="nav-link">← Website</a>
            </div>
            
            <!-- MAIN LAYOUT -->
            <div class="main-content">
                
                <div class="player-container">
                    <h1 class="station-name">FRAWO FUNK</h1>
                    <div style="color: #aaa; font-size: 16px; font-weight: 300; letter-spacing: 1px; text-transform: uppercase;">Underground Electronic Broadcast</div>
                    
                    <div class="now-playing">
                        <div class="np-label">Now Playing</div>
                        <div class="np-title" id="np-title">Loading...</div>
                        <div class="np-artist" id="np-artist">FraWo Auto-DJ</div>
                    </div>
                    
                    <div class="controls-wrapper">
                        <div class="play-ring">
                            <div class="ripple" id="play-ripple"></div>
                            <button id="main-play-btn" class="play-btn">
                                <svg id="icon-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                                <svg id="icon-pause" viewBox="0 0 24 24" style="display:none;"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                            </button>
                        </div>
                        
                        <div class="status-indicator">
                            <div class="status-badge" id="status-badge">
                                <span class="status-dot"></span>
                                <span id="stream-status">Offline</span>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 8px; margin-left: 5px;">HQ AUDIO // 320 KBPS</div>
                        </div>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="sidebar-title">The Community</div>
                    
                    <div class="chat-container">
                        <div class="chat-messages" id="chat-messages">
                            <div class="chat-msg"><span class="msg-sys">TheMachine:</span> Welcome to the underground.</div>
                            <div class="chat-msg"><span class="msg-sys">TheMachine:</span> Live-Chat is in read-only mode for guests.</div>
                        </div>
                        <div class="chat-input-area">
                            <input type="text" class="chat-input" placeholder="Join to chat..." disabled="disabled"/>
                        </div>
                    </div>
                    
                    <div class="auth-panel">
                        <t t-if="request.env.user.id == request.env.ref('base.public_user').id">
                            <!-- NOT LOGGED IN -->
                            <div style="font-size: 12px; color: #aaa; margin-bottom: 15px; line-height: 1.5;">
                                Registriere dich kostenlos, um im Chat zu schreiben und exklusiven Zugang zu bekommen.
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                <a href="/web/signup?redirect=/frawo-funk" class="btn-action btn-primary">Kostenlos Registrieren</a>
                                <a href="/web/login?redirect=/frawo-funk" class="btn-action btn-outline">VIP Login</a>
                            </div>
                        </t>
                        <t t-else="">
                            <!-- LOGGED IN -->
                            <div class="user-profile">
                                <img t-attf-src="/web/image/res.users/{{request.env.user.id}}/avatar_128" class="user-avatar"/>
                                <div>
                                    <div style="font-size: 10px; color: #10B981; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;">VIP Access</div>
                                    <div style="font-weight: 700; font-size: 16px;"><t t-esc="request.env.user.name"/></div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; font-size: 12px; color: #888; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                                Deine Verbindung zum Studio steht. (Chat-Send-Funktion in Kürze verfügbar).
                            </div>
                        </t>
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
                const playRipple = document.getElementById('play-ripple');
                const iconPlay = document.getElementById('icon-play');
                const iconPause = document.getElementById('icon-pause');
                const statusBadge = document.getElementById('status-badge');
                const streamStatus = document.getElementById('stream-status');
                const bgDynamic = document.getElementById('bg-dynamic');
                
                const npTitle = document.getElementById('np-title');
                const npArtist = document.getElementById('np-artist');
                
                // Canvas Setup
                const canvas = document.getElementById('canvas-visualizer');
                const ctx = canvas.getContext('2d');
                let cw, ch;
                
                function resizeCanvas() {
                    cw = canvas.width = window.innerWidth;
                    ch = canvas.height = canvas.offsetHeight;
                }
                window.addEventListener('resize', resizeCanvas);
                resizeCanvas();
                
                // Fetch AzuraCast Now Playing
                function fetchNowPlaying() {
                    fetch('https://funk.frawo-tech.de/api/nowplaying/1')
                        .then(r => r.json())
                        .then(d => {
                            if(d && d.now_playing && d.now_playing.song) {
                                npTitle.innerText = d.now_playing.song.title || 'Unknown Title';
                                npArtist.innerText = d.now_playing.song.artist || 'Unknown Artist';
                            }
                        }).catch(e => console.log('API Error:', e));
                }
                fetchNowPlaying();
                setInterval(fetchNowPlaying, 15000);
                
                // Web Audio API
                let audioCtx, analyser, source;
                let dataArray, freqArray, bufferLength;
                let isPlaying = false;
                let useFallback = false;
                let animFrame;
                
                function initAudio() {
                    if (!audioCtx) {
                        try {
                            const AudioContext = window.AudioContext || window.webkitAudioContext;
                            audioCtx = new AudioContext();
                            analyser = audioCtx.createAnalyser();
                            analyser.fftSize = 2048; // Detailed waveform
                            bufferLength = analyser.frequencyBinCount;
                            dataArray = new Uint8Array(bufferLength);
                            freqArray = new Uint8Array(bufferLength);
                            
                            source = audioCtx.createMediaElementSource(audio);
                            source.connect(analyser);
                            analyser.connect(audioCtx.destination);
                        } catch (e) {
                            console.error("CORS blocked Web Audio API", e);
                            useFallback = true;
                        }
                    }
                    if(audioCtx && audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                }
                
                // Draw Oscilloscope
                function draw() {
                    if(!isPlaying) return;
                    
                    animFrame = requestAnimationFrame(draw);
                    
                    ctx.clearRect(0, 0, cw, ch);
                    
                    // Draw glow
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = '#10B981';
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#10B981';
                    
                    ctx.beginPath();
                    
                    let bassEnergy = 0;
                    
                    if(!useFallback && analyser) {
                        analyser.getByteTimeDomainData(dataArray);
                        analyser.getByteFrequencyData(freqArray);
                        
                        // Check if we actually get data (CORS block after init test)
                        let hasData = false;
                        let sliceWidth = cw * 1.0 / bufferLength;
                        let x = 0;
                        
                        for(let i = 0; i < bufferLength; i++) {
                            let v = dataArray[i] / 128.0;
                            if(v !== 1.0) hasData = true; // 128 is silence in TimeDomain
                            
                            let y = v * ch / 2;
                            if(i === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                            x += sliceWidth;
                            
                            // Calc Bass Energy from first 10 frequency bins
                            if(i < 10) {
                                bassEnergy += freqArray[i];
                            }
                        }
                        ctx.lineTo(cw, ch / 2);
                        ctx.stroke();
                        
                        if(!hasData && audio.currentTime > 2) {
                            useFallback = true;
                        }
                        
                        bassEnergy = bassEnergy / 10; // average
                    } else {
                        // Fake visualizer (sine wave)
                        let time = Date.now() / 200;
                        ctx.moveTo(0, ch/2);
                        for(let i=0; i<cw; i+=5) {
                            let y = ch/2 + Math.sin(i*0.02 + time) * 30 * Math.sin(time*0.5) + Math.cos(i*0.05 - time)*10;
                            ctx.lineTo(i, y);
                        }
                        ctx.stroke();
                        bassEnergy = 120 + Math.sin(time)*50; // fake bass
                    }
                    
                    // Audio Reactivity
                    // Ripple effect around play button based on bass
                    if(bassEnergy > 150) {
                        let scale = 1 + (bassEnergy - 150) / 100; // max scale ~2
                        playRipple.style.opacity = '0.8';
                        playRipple.style.width = (90 * scale) + 'px';
                        playRipple.style.height = (90 * scale) + 'px';
                        
                        // Pulse background
                        let intensity = (bassEnergy - 150) / 100; // 0 to ~1
                        let r1 = 15 + intensity * 20; // 15% to 35%
                        let r2 = 5 + intensity * 15; // 5% to 20%
                        bgDynamic.style.background = `radial-gradient(circle at 50% 50%, rgba(139,92,246,${r1/100}) 0%, rgba(16,185,129,${r2/100}) 40%, rgba(3,3,3,1) 80%)`;
                    } else {
                        playRipple.style.opacity = '0';
                        playRipple.style.width = '90px';
                        playRipple.style.height = '90px';
                        bgDynamic.style.background = `radial-gradient(circle at 50% 50%, rgba(139,92,246,0.15) 0%, rgba(16,185,129,0.05) 40%, rgba(3,3,3,1) 80%)`;
                    }
                }
                
                playBtn.addEventListener('click', function() {
                    if(isPlaying) {
                        audio.pause();
                        isPlaying = false;
                        cancelAnimationFrame(animFrame);
                        
                        iconPlay.style.display = 'block';
                        iconPause.style.display = 'none';
                        playBtn.classList.remove('playing');
                        statusBadge.classList.remove('live');
                        streamStatus.innerText = 'OFFLINE';
                        
                        playRipple.style.opacity = '0';
                        ctx.clearRect(0, 0, cw, ch);
                        bgDynamic.style.background = `radial-gradient(circle at 50% 50%, rgba(139,92,246,0.15) 0%, rgba(16,185,129,0.05) 40%, rgba(3,3,3,1) 80%)`;
                    } else {
                        initAudio();
                        audio.play().then(() => {
                            isPlaying = true;
                            iconPlay.style.display = 'none';
                            iconPause.style.display = 'block';
                            playBtn.classList.add('playing');
                            statusBadge.classList.add('live');
                            streamStatus.innerText = 'ON AIR';
                            draw();
                        }).catch(e => {
                            console.error("Audio block:", e);
                            streamStatus.innerText = 'PLAY ERROR';
                        });
                    }
                });
                
                // Simple Parallax Effect on background text
                document.addEventListener('mousemove', function(e) {
                    const bgText = document.querySelector('.bg-text');
                    const x = (e.clientX / window.innerWidth - 0.5) * 40;
                    const y = (e.clientY / window.innerHeight - 0.5) * 40;
                    bgText.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
                });
            });
            // ]]>
        </script>
    </t>
</t>"""

existing_view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search_read', [[('key', '=', 'website.frawo_radio_page')]], {'fields': ['id']})
if existing_view:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [existing_view[0]['id'], {'arch': live_html}])
    print("SUCCESS: Updated Ultra-Premium Dynamic NTS Style Radio page.")
else:
    print("ERROR: View 'website.frawo_radio_page' not found!")
