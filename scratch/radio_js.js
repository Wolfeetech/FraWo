
            // 
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
                        .then(r =&gt; r.json())
                        .then(d =&gt; {
                            if(d &amp;&amp; d.now_playing &amp;&amp; d.now_playing.song) {
                                npTitle.innerText = d.now_playing.song.title || 'Unknown Title';
                                npArtist.innerText = d.now_playing.song.artist || 'Unknown Artist';
                            }
                        }).catch(e =&gt; console.log('API Error:', e));
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
                    if(audioCtx &amp;&amp; audioCtx.state === 'suspended') {
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
                    
                    if(!useFallback &amp;&amp; analyser) {
                        analyser.getByteTimeDomainData(dataArray);
                        analyser.getByteFrequencyData(freqArray);
                        
                        // Check if we actually get data (CORS block after init test)
                        let hasData = false;
                        let sliceWidth = cw * 1.0 / bufferLength;
                        let x = 0;
                        
                        for(let i = 0; i &lt; bufferLength; i++) {
                            let v = dataArray[i] / 128.0;
                            if(v !== 1.0) hasData = true; // 128 is silence in TimeDomain
                            
                            let y = v * ch / 2;
                            if(i === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                            x += sliceWidth;
                            
                            // Calc Bass Energy from first 10 frequency bins
                            if(i &lt; 10) {
                                bassEnergy += freqArray[i];
                            }
                        }
                        ctx.lineTo(cw, ch / 2);
                        ctx.stroke();
                        
                        if(!hasData &amp;&amp; audio.currentTime &gt; 2) {
                            useFallback = true;
                        }
                        
                        bassEnergy = bassEnergy / 10; // average
                    } else {
                        // Fake visualizer (sine wave)
                        let time = Date.now() / 200;
                        ctx.moveTo(0, ch/2);
                        for(let i=0; i&lt;cw; i+=5) {
                            let y = ch/2 + Math.sin(i*0.02 + time) * 30 * Math.sin(time*0.5) + Math.cos(i*0.05 - time)*10;
                            ctx.lineTo(i, y);
                        }
                        ctx.stroke();
                        bassEnergy = 120 + Math.sin(time)*50; // fake bass
                    }
                    
                    // Audio Reactivity
                    // Ripple effect around play button based on bass
                    if(bassEnergy &gt; 150) {
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
                        audio.play().then(() =&gt; {
                            isPlaying = true;
                            iconPlay.style.display = 'none';
                            iconPause.style.display = 'block';
                            playBtn.classList.add('playing');
                            statusBadge.classList.add('live');
                            streamStatus.innerText = 'ON AIR';
                            draw();
                        }).catch(e =&gt; {
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
            // 
        