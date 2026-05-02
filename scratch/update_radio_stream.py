import xmlrpc.client
import sys

url = 'http://10.1.0.22:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'Wolf2024!Frawo'

FOOTER_HTML = '''
<div class="fw-radio-sticky">
  <div class="container">
    <div class="fw-radio-inner">
      <div class="fw-radio-info">
        <div class="fw-radio-visualizer">
          <div class="fw-radio-bar" style="animation-delay: 0s;"></div>
          <div class="fw-radio-bar" style="animation-delay: 0.2s;"></div>
          <div class="fw-radio-bar" style="animation-delay: 0.1s;"></div>
        </div>
        <div>
          <div style="font-size: 0.7rem; color: var(--fw-text-dimmer); text-transform: uppercase; letter-spacing: 0.05em;">FraWo Funk — Live</div>
          <div id="radio-track" style="font-size: 0.85rem; color: var(--fw-text); font-weight: 500;">Connecting...</div>
        </div>
      </div>
      <div class="fw-radio-controls">
        <button id="radio-toggle" class="fw-radio-btn">
          <i class="fa fa-play"></i>
        </button>
      </div>
    </div>
  </div>
</div>

<section class="fw-footer" style="margin-bottom: 60px;">
  <div class="container">
    <div class="row align-items-center py-4 border-top" style="border-color: rgba(255,255,255,0.1) !important;">
      <div class="col-md-6 text-center text-md-start">
        <span style="color: var(--fw-text-dimmer); font-size: 0.8rem;">© 2026 FraWo GbR. State-of-the-Art Media &amp; Event.</span>
      </div>
      <div class="col-md-6 text-center text-md-end">
        <ul class="list-inline mb-0" style="font-size: 0.8rem;">
          <li class="list-inline-item"><a href="/impressum" style="color: var(--fw-text-dim); text-decoration: none;">Impressum</a></li>
          <li class="list-inline-item ms-3"><a href="/datenschutz" style="color: var(--fw-text-dim); text-decoration: none;">Datenschutz</a></li>
          <li class="list-inline-item ms-3"><a href="/contactus" style="color: var(--fw-text-dim); text-decoration: none;">Kontakt</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<script>
  (function() {
    const audio = new Audio('https://radio.yourparty.tech/listen/radio.yourparty/radio.mp3');
    const btn = document.getElementById('radio-toggle');
    const track = document.getElementById('radio-track');
    if (!btn || !track) return;
    
    btn.onclick = () => {
      if (audio.paused) {
        audio.play();
        btn.innerHTML = '<i class="fa fa-pause"></i>';
      } else {
        audio.pause();
        btn.innerHTML = '<i class="fa fa-play"></i>';
      }
    };

    const tracks = ["NTS Radio Mix", "Stockenweiler Sessions", "Electronic Deep Dive", "FraWo Night Drive"];
    setInterval(() => {
      if (!audio.paused) {
        track.innerText = tracks[Math.floor(Math.random() * tracks.length)];
      }
    }, 10000);
  })();
</script>
'''

def run():
    print(f"Connecting to Odoo at {url}...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        print("[X] Auth failed")
        return
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    radio_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[['key', '=', 'website.frawo_radio_footer']]])
    
    arch = f"""<data inherit_id="website.layout" name="FraWo Radio Footer">
        <xpath expr="//div[@id='footer']" position="inside">
            {FOOTER_HTML}
        </xpath>
    </data>"""

    if radio_view_ids:
        print(f"Updating existing Radio Footer view {radio_view_ids[0]}")
        models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[radio_view_ids[0]], {'arch_db': arch, 'active': True}])
    else:
        print("View not found!")

if __name__ == "__main__":
    run()
