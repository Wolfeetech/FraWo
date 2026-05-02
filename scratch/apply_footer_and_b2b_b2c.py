import xmlrpc.client
import sys
import os

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
    const audio = new Audio('https://radio.frawo-tech.de/listen/frawo_funk/radio.mp3');
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
    
    # 1. Update B2B and B2C pages
    print("Reading B2B and B2C blocks...")
    with open('C:\\WORKSPACE\\FraWo\\Codex\\website\\frawo_b2b_blocks.html', 'r', encoding='utf-8') as f:
        b2b_html = f.read()
    with open('C:\\WORKSPACE\\FraWo\\Codex\\website\\frawo_b2c_blocks.html', 'r', encoding='utf-8') as f:
        b2c_html = f.read()

    # Get the image attachments if needed (assuming they are still there from previous run)
    att_b2b = models.execute_kw(db, uid, password, 'ir.attachment', 'search', [[['name', '=', 'b2b_lifestyle.png']]])
    att_b2c = models.execute_kw(db, uid, password, 'ir.attachment', 'search', [[['name', '=', 'b2c_lifestyle.png']]])
    
    if att_b2b: b2b_html = b2b_html.replace('__IMG_ABOUT_CONSOLE__', f'/web/image/{att_b2b[0]}')
    if att_b2c: b2c_html = b2c_html.replace('__IMG_SERVICE_STAGE__', f'/web/image/{att_b2c[0]}')

    # Update B2C
    b2c_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[['key', '=', 'website.page_b2c']]])
    if b2c_view_ids:
        print(f"Updating B2C Page View {b2c_view_ids[0]}...")
        b2c_arch = f'<t t-name="website.b2c"><t t-call="website.layout"><div id="wrap" class="oe_structure oe_empty">{b2c_html}</div></t></t>'
        models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[b2c_view_ids[0]], {'arch_db': b2c_arch}])
    
    # Update B2B
    b2b_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[['key', '=', 'website.page_b2b']]])
    if b2b_view_ids:
        print(f"Updating B2B Page View {b2b_view_ids[0]}...")
        b2b_arch = f'<t t-name="website.b2b"><t t-call="website.layout"><div id="wrap" class="oe_structure oe_empty">{b2b_html}</div></t></t>'
        models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[b2b_view_ids[0]], {'arch_db': b2b_arch}])

    # 2. Inject Radio Player Footer safely via inherited view
    # Find layout ID
    layout_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[['key', '=', 'website.layout']]])
    if not layout_ids:
        print("[X] Could not find website.layout")
        return
    
    layout_id = layout_ids[0]
    print(f"website.layout is ID {layout_id}")

    # Check if our custom radio view already exists
    radio_view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[['key', '=', 'website.frawo_radio_footer']]])
    
    arch = f'''
    <data inherit_id="website.layout" name="FraWo Radio Footer">
        <xpath expr="//div[@id='footer']" position="inside">
            {FOOTER_HTML}
        </xpath>
    </data>
    '''

    if radio_view_ids:
        print(f"Updating existing Radio Footer view {radio_view_ids[0]}")
        models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[radio_view_ids[0]], {'arch_db': arch, 'active': True}])
    else:
        print("Creating new Radio Footer view")
        models.execute_kw(db, uid, password, 'ir.ui.view', 'create', [{
            'name': 'FraWo Radio Footer',
            'type': 'qweb',
            'mode': 'extension',
            'inherit_id': layout_id,
            'key': 'website.frawo_radio_footer',
            'active': True,
            'arch': arch
        }])

    print("Done!")

if __name__ == "__main__":
    run()
