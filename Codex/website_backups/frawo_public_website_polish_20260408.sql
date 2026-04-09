BEGIN;

UPDATE ir_config_parameter
SET value = 'https://www.frawo-tech.de'
WHERE key = 'web.base.url';

UPDATE ir_config_parameter
SET value = 'True'
WHERE key = 'web.base.url.freeze';

UPDATE website
SET domain = NULL,
    homepage_url = '/'
WHERE id = 1;

UPDATE ir_ui_view
SET active = FALSE
WHERE id = 3699;

UPDATE ir_ui_view
SET active = FALSE
WHERE id = 4450;

UPDATE ir_ui_view
SET active = TRUE,
    arch_db = jsonb_build_object(
        'de_DE',
        $$<data inherit_id="website.layout" name="Default" active="True">
  <xpath expr="//div[@id='footer']" position="replace">
    <div id="footer" class="oe_structure oe_structure_solo" t-ignore="true" t-if="not no_footer">
      <section class="s_text_block pt40 pb24" data-snippet="s_text_block" data-name="Text" style="background:#064e3b; color:#f0fdf4;">
        <div class="container">
          <div class="row g-4 align-items-start">
            <div class="col-lg-4">
              <h4 class="mb-3" style="color:#ffffff;">FraWo GbR</h4>
              <p class="mb-0">Smart Media &amp; Event mit klarer technischer Handschrift: Website, digitale Betriebsablaeufe und ein eigener Medienpfad, der nicht nur auf dem Papier funktioniert.</p>
            </div>
            <div class="col-lg-3">
              <h5 class="mb-3" style="color:#a7f3d0;">Direktwege</h5>
              <ul class="list-unstyled mb-0">
                <li class="mb-2"><a href="/" style="color:#ffffff;">Startseite</a></li>
                <li class="mb-2"><a href="mailto:info@frawo-tech.de" style="color:#ffffff;">Projekt anfragen</a></li>
                <li><a href="/radio/public/frawo-funk" style="color:#ffffff;">FraWo Funk</a></li>
              </ul>
            </div>
            <div class="col-lg-5">
              <h5 class="mb-3" style="color:#a7f3d0;">Kontakt</h5>
              <ul class="list-unstyled mb-0">
                <li class="mb-2">Rothkreuz 14, 88138 Weissensberg</li>
                <li class="mb-2"><a href="tel:+4915155243164" style="color:#ffffff;">+49 151 55243164</a></li>
                <li><a href="mailto:info@frawo-tech.de" style="color:#ffffff;">info@frawo-tech.de</a></li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  </xpath>
</data>$$,
        'en_US',
        $$<data inherit_id="website.layout" name="Default" active="True">
  <xpath expr="//div[@id='footer']" position="replace">
    <div id="footer" class="oe_structure oe_structure_solo" t-ignore="true" t-if="not no_footer">
      <section class="s_text_block pt40 pb24" data-snippet="s_text_block" data-name="Text" style="background:#064e3b; color:#f0fdf4;">
        <div class="container">
          <div class="row g-4 align-items-start">
            <div class="col-lg-4">
              <h4 class="mb-3" style="color:#ffffff;">FraWo GbR</h4>
              <p class="mb-0">Smart Media &amp; Event with a clear technical backbone: website, digital operations and a media path that is built to work in real life.</p>
            </div>
            <div class="col-lg-3">
              <h5 class="mb-3" style="color:#a7f3d0;">Direct paths</h5>
              <ul class="list-unstyled mb-0">
                <li class="mb-2"><a href="/" style="color:#ffffff;">Homepage</a></li>
                <li class="mb-2"><a href="mailto:info@frawo-tech.de" style="color:#ffffff;">Start a project</a></li>
                <li><a href="/radio/public/frawo-funk" style="color:#ffffff;">FraWo Funk</a></li>
              </ul>
            </div>
            <div class="col-lg-5">
              <h5 class="mb-3" style="color:#a7f3d0;">Contact</h5>
              <ul class="list-unstyled mb-0">
                <li class="mb-2">Rothkreuz 14, 88138 Weissensberg</li>
                <li class="mb-2"><a href="tel:+4915155243164" style="color:#ffffff;">+49 151 55243164</a></li>
                <li><a href="mailto:info@frawo-tech.de" style="color:#ffffff;">info@frawo-tech.de</a></li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  </xpath>
</data>$$
    )
WHERE id = 4405;

UPDATE website_menu
SET name = '{"de_DE":"Projekt anfragen","en_US":"Start a project"}'::jsonb,
    url = 'mailto:info@frawo-tech.de',
    page_id = NULL,
    new_window = TRUE
WHERE id IN (3, 6);

UPDATE ir_ui_view
SET arch_db = jsonb_build_object(
        'de_DE',
        $$<data inherit_id="website.placeholder_header_call_to_action" name="Header Call to Action" active="True">
  <xpath expr="." position="inside">
    <li t-attf-class="#{_item_class}">
      <div t-attf-class="oe_structure oe_structure_solo #{_div_class}" class="oe_structure oe_structure_solo">
        <section class="oe_unremovable oe_unmovable s_text_block o_colored_level" data-snippet="s_text_block" data-name="Text" style="background-image: none;">
          <div class="container">
            <a href="mailto:info@frawo-tech.de" class="oe_unremovable btn btn-primary btn_cta" data-bs-original-title="" title="">Projekt anfragen</a>
          </div>
        </section>
      </div>
    </li>
  </xpath>
</data>$$,
        'en_US',
        $$<data inherit_id="website.placeholder_header_call_to_action" name="Header Call to Action" active="True">
  <xpath expr="." position="inside">
    <li t-attf-class="#{_item_class}">
      <div t-attf-class="oe_structure oe_structure_solo #{_div_class}" class="oe_structure oe_structure_solo">
        <section class="oe_unremovable oe_unmovable s_text_block o_colored_level" data-snippet="s_text_block" data-name="Text" style="background-image: none;">
          <div class="container">
            <a href="mailto:info@frawo-tech.de" class="oe_unremovable btn btn-primary btn_cta" data-bs-original-title="" title="">Start a project</a>
          </div>
        </section>
      </div>
    </li>
  </xpath>
</data>$$
    )
WHERE id = 4462;

UPDATE ir_ui_view
SET arch_db = jsonb_build_object(
        'de_DE',
        $$<data inherit_id="website.placeholder_header_call_to_action" name="Header Call to Action" active="True">
  <xpath expr="." position="inside">
    <li t-attf-class="#{_item_class}">
      <div t-attf-class="oe_structure oe_structure_solo #{_div_class}">
        <section class="oe_unremovable oe_unmovable s_text_block" data-snippet="s_text_block" data-name="Text">
          <div class="container">
            <a href="mailto:info@frawo-tech.de" class="oe_unremovable btn btn-primary btn_cta">Projekt anfragen</a>
          </div>
        </section>
      </div>
    </li>
  </xpath>
</data>$$,
        'en_US',
        $$<data inherit_id="website.placeholder_header_call_to_action" name="Header Call to Action" active="True">
  <xpath expr="." position="inside">
    <li t-attf-class="#{_item_class}">
      <div t-attf-class="oe_structure oe_structure_solo #{_div_class}">
        <section class="oe_unremovable oe_unmovable s_text_block" data-snippet="s_text_block" data-name="Text">
          <div class="container">
            <a href="mailto:info@frawo-tech.de" class="oe_unremovable btn btn-primary btn_cta">Start a project</a>
          </div>
        </section>
      </div>
    </li>
  </xpath>
</data>$$
    )
WHERE id = 3726;

UPDATE ir_ui_view
SET arch_db = jsonb_build_object(
        'de_DE',
        $$<t name="Contact Us" t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <style>
        .frawo-contact-hero{background:linear-gradient(135deg,#064e3b 0%,#14532d 55%,#052e16 100%);color:#f0fdf4;position:relative;overflow:hidden;}
        .frawo-contact-hero:before{content:"";position:absolute;inset:auto -8% -35% auto;width:28rem;height:28rem;border-radius:50%;background:radial-gradient(circle,#a855f755 0%,#a855f700 72%);}
        .frawo-contact-card{border:none;border-radius:1.4rem;background:#ffffff;box-shadow:0 24px 60px rgba(6,78,59,.10);height:100%;}
        .frawo-contact-card h3{color:#064e3b;font-weight:800;}
        .frawo-contact-kicker{letter-spacing:.22em;text-transform:uppercase;color:#a7f3d0;font-weight:700;font-size:.82rem;}
        .frawo-contact-btn{background:#064e3b;border-color:#064e3b;}
      </style>
      <section class="frawo-contact-hero pt96 pb96">
        <div class="container position-relative">
          <div class="row align-items-center g-4">
            <div class="col-lg-8">
              <div class="frawo-contact-kicker mb-3">FraWo Kontakt</div>
              <h1 class="display-4 mb-3">Direkter Draht statt Kontaktformular-Zirkus.</h1>
              <p class="lead mb-0">Wenn es um Website, digitale Betriebsablaeufe oder Medienpfade geht, ist Mail aktuell der schnellste Einstieg. Fuer kurze Rueckfragen geht auch der direkte Telefonpfad.</p>
            </div>
            <div class="col-lg-4 text-lg-end">
              <a class="btn btn-light btn-lg me-2 mb-2" href="mailto:info@frawo-tech.de">info@frawo-tech.de</a>
              <a class="btn btn-outline-light btn-lg mb-2" href="/radio/public/frawo-funk">FraWo Funk</a>
            </div>
          </div>
        </div>
      </section>
      <section class="pt64 pb96">
        <div class="container">
          <div class="row g-4">
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">E-Mail</h3>
                <p class="mb-3">Projektanfragen, Rueckfragen und Abstimmungen laufen aktuell am saubersten per Mail.</p>
                <p class="mb-0"><a href="mailto:info@frawo-tech.de">info@frawo-tech.de</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">Telefon</h3>
                <p class="mb-3">Wenn etwas schnell geklaert werden soll, ist der direkte Operator-Pfad offen.</p>
                <p class="mb-0"><a href="tel:+4915155243164">+49 151 55243164</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">Standort</h3>
                <p class="mb-3">FraWo sitzt in Weissensberg und baut von dort Medien-, Website- und Betriebsprozesse mit Bodenhaftung.</p>
                <p class="mb-0">Rothkreuz 14<br/>88138 Weissensberg</p>
              </div>
            </div>
          </div>
          <div class="row g-5 align-items-center pt64">
            <div class="col-lg-7">
              <h2 class="display-6 mb-3" style="color:#064e3b;font-weight:900;">Womit koennen wir helfen?</h2>
              <p class="mb-3">FraWo verbindet Marke, Betrieb und Medienpraesenz. Entsprechend hilfreich ist eine kurze Mail mit Kontext: Was soll live gehen, was soll stabiler werden, und welche Rolle spielt die Website oder der Medienpfad dabei?</p>
              <p class="mb-0">Wenn du direkt loslegen willst, nimm den Mailpfad. Fuer einen ersten Eindruck der Medienlinie gibt es den Radio-Einstieg direkt auf der Website.</p>
            </div>
            <div class="col-lg-5">
              <div class="card frawo-contact-card p-4 p-lg-5">
                <h3 class="h3 mb-3">Naechster Schritt</h3>
                <p class="mb-4">Schreib kurz, worum es geht. Wir ordnen den Fall sauber ein und melden uns auf dem passenden Weg zurueck.</p>
                <div class="d-flex flex-wrap gap-3">
                  <a class="btn btn-primary frawo-contact-btn" href="mailto:info@frawo-tech.de?subject=FraWo%20Projektanfrage">Projekt anfragen</a>
                  <a class="btn btn-outline-secondary" href="/">Zur Startseite</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>$$,
        'en_US',
        $$<t name="Contact Us" t-name="website.contactus">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <style>
        .frawo-contact-hero{background:linear-gradient(135deg,#064e3b 0%,#14532d 55%,#052e16 100%);color:#f0fdf4;position:relative;overflow:hidden;}
        .frawo-contact-hero:before{content:"";position:absolute;inset:auto -8% -35% auto;width:28rem;height:28rem;border-radius:50%;background:radial-gradient(circle,#a855f755 0%,#a855f700 72%);}
        .frawo-contact-card{border:none;border-radius:1.4rem;background:#ffffff;box-shadow:0 24px 60px rgba(6,78,59,.10);height:100%;}
        .frawo-contact-card h3{color:#064e3b;font-weight:800;}
        .frawo-contact-kicker{letter-spacing:.22em;text-transform:uppercase;color:#a7f3d0;font-weight:700;font-size:.82rem;}
        .frawo-contact-btn{background:#064e3b;border-color:#064e3b;}
      </style>
      <section class="frawo-contact-hero pt96 pb96">
        <div class="container position-relative">
          <div class="row align-items-center g-4">
            <div class="col-lg-8">
              <div class="frawo-contact-kicker mb-3">FraWo Contact</div>
              <h1 class="display-4 mb-3">A direct line, not a maze of forms.</h1>
              <p class="lead mb-0">For website, digital operations or media-path work, email is currently the fastest way in. Short questions can also go through the direct phone path.</p>
            </div>
            <div class="col-lg-4 text-lg-end">
              <a class="btn btn-light btn-lg me-2 mb-2" href="mailto:info@frawo-tech.de">info@frawo-tech.de</a>
              <a class="btn btn-outline-light btn-lg mb-2" href="/radio/public/frawo-funk">FraWo Funk</a>
            </div>
          </div>
        </div>
      </section>
      <section class="pt64 pb96">
        <div class="container">
          <div class="row g-4">
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">Email</h3>
                <p class="mb-3">Project requests, follow-ups and coordination currently work best via email.</p>
                <p class="mb-0"><a href="mailto:info@frawo-tech.de">info@frawo-tech.de</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">Phone</h3>
                <p class="mb-3">If something needs a quick answer, the direct operator path is available.</p>
                <p class="mb-0"><a href="tel:+4915155243164">+49 151 55243164</a></p>
              </div>
            </div>
            <div class="col-lg-4 d-flex">
              <div class="card frawo-contact-card p-4">
                <h3 class="h4 mb-3">Location</h3>
                <p class="mb-3">FraWo operates from Weissensberg and builds media, website and business-process paths with real-world grounding.</p>
                <p class="mb-0">Rothkreuz 14<br/>88138 Weissensberg</p>
              </div>
            </div>
          </div>
          <div class="row g-5 align-items-center pt64">
            <div class="col-lg-7">
              <h2 class="display-6 mb-3" style="color:#064e3b;font-weight:900;">What do you need help with?</h2>
              <p class="mb-3">FraWo connects brand, operations and media presence. A short email with context helps most: what needs to go live, what should become more reliable, and how the website or media path fits into it.</p>
              <p class="mb-0">If you want to get started right away, use the email path. For a first impression of the media line, the radio entry is already live on the website.</p>
            </div>
            <div class="col-lg-5">
              <div class="card frawo-contact-card p-4 p-lg-5">
                <h3 class="h3 mb-3">Next step</h3>
                <p class="mb-4">Send a short note about the request. We will sort it cleanly and come back through the right path.</p>
                <div class="d-flex flex-wrap gap-3">
                  <a class="btn btn-primary frawo-contact-btn" href="mailto:info@frawo-tech.de?subject=FraWo%20Project%20Request">Start a project</a>
                  <a class="btn btn-outline-secondary" href="/">Back to homepage</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>$$
    )
WHERE id = 3637;

COMMIT;
