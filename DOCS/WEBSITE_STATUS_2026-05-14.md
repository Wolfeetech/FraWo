# FraWo Website Status - 2026-05-14

## Live URL
https://www.frawo-tech.de/

## Completed ✅

### Design & Branding
- [x] New CI: Purple (#9d4edd) primary, Tundra Grey (#6b7067) accent
- [x] Professional typography (Inter, weights 300-800)
- [x] kabaus.at + NTS Radio inspired minimal design
- [x] Dark theme (#0a0a0a background)
- [x] Professional spacing scale (CSS custom properties)
- [x] Consistent 1px borders throughout

### Content
- [x] Hero section: "Licht & Ton für dein Event"
- [x] 4 Service cards with background images
  - Licht & Ton (Mikrofon image)
  - Verleih (Fußballdart image)
  - Stage Service (FOH image)
  - Sonderbauten (Holzkonstruktion image)
- [x] Referenzen (8 clients in 4×2 grid)
- [x] Projekte (3 image cards: Rave on SUP, Sonderbau, Live Stage)
- [x] Über Uns (Wolf + Franz)
- [x] Radio CTA (FraWo Funk)
- [x] Final CTA

### SEO
- [x] Meta Title: "FraWo Veranstaltungstechnik Bodensee | Licht & Ton für Events"
- [x] Meta Description (160 chars, keyword-optimized)
- [x] Meta Keywords
- [x] Schema.org LocalBusiness JSON-LD (with phone, email, geo coordinates)
- [x] Service catalog in structured data
- [x] Open Graph tags (Facebook, LinkedIn)
- [x] Twitter Card tags
- [x] robots.txt (allows crawling, references sitemap)
- [x] sitemap.xml (8 pages, priority-weighted)

### Performance
- [x] Lazy loading on all images (except hero)
- [x] CSS custom properties for performance
- [x] Optimized font loading (Google Fonts)
- [x] Minimal JavaScript
- [x] WebP images with picture element fallbacks (10-50% size reduction)
- [x] Optimized JPG compression (quality 85, max-width 1920px)

### Legal
- [x] Impressum (Rothkreuz 14, Weissensberg)
- [x] Datenschutz (DSGVO-compliant)

### Technical
- [x] Responsive design (768px, 991px breakpoints)
- [x] Mobile-optimized
- [x] Professional hover effects
- [x] Smooth animations (cubic-bezier)
- [x] Focus indicators (WCAG 2.1 compliant)
- [x] Skip-to-content link
- [x] Resource hints (preconnect, preload)
- [x] Perfect heading hierarchy (H1→H2→H3)

## Images Uploaded

| ID   | Filename              | Usage                | WebP ID |
|------|-----------------------|----------------------|---------|
| 993  | hero-bodensee.jpg     | Hero section         | 1003    |
| 994  | service-ton.jpg       | (unused)             | -       |
| 995  | service-stage.jpg     | Stage Service card + Projects | 1004 |
| 996  | sonderbau-holz.jpg    | Sonderbauten card + Projects | 1005 |
| 997  | rave-on-sup.jpg       | Projects section     | 1006    |
| 998  | buehne-traverse.jpg   | Über Uns section     | 1007    |
| 999  | fussballdart.jpg      | Verleih card         | 1008    |
| 1000 | mikrofon-ton.jpg      | Licht & Ton card     | 1009    |
| 1001 | robots.txt            | SEO crawl rules      | -       |
| 1002 | sitemap.xml           | SEO site structure   | -       |

## To Do 📋

### High Priority
- [x] Add phone number to Schema.org markup
- [x] Optimize images (compress, WebP format)
- [x] Create robots.txt for search engines
- [x] Generate sitemap.xml
- [x] WebP images with picture element fallbacks
- [ ] Submit sitemap to Google Search Console (manual step)
- [ ] Test Google PageSpeed Insights (API rate-limited, try manually)

### Medium Priority
- [x] Add more alt text descriptions (SEO-optimized)
- [x] ARIA labels for all interactive elements
- [x] Semantic section labels (accessibility)
- [ ] Run WAVE accessibility evaluation
- [ ] Test with screen readers (NVDA, JAWS)
- [ ] Create dedicated service pages (/services/licht-ton, etc.)
- [ ] Add testimonials section
- [ ] Add pricing page (if applicable)

### Low Priority
- [ ] Add animations library (AOS, Framer Motion)
- [ ] Add cookie consent banner (if tracking added)
- [ ] Add blog/news section
- [ ] Multi-language support (EN)

## Scripts Available

```bash
# Deploy homepage HTML
python scripts/deploy_new_homepage.py

# Upload CSS
python scripts/upload_css_to_odoo.py

# Generate legal pages
python scripts/generate_legal_pages.py

# Upload images
python scripts/upload_images_to_odoo.py

# Add SEO metadata
python scripts/add_seo_metadata.py

# Add Open Graph tags
python scripts/add_open_graph_tags.py

# Check CSS in Odoo
python scripts/check_css_in_odoo.py

# Create robots.txt
python scripts/create_robots_txt.py

# Generate sitemap.xml
python scripts/create_sitemap_xml.py

# Optimize images (WebP conversion)
python scripts/optimize_images_webp.py

# Test PageSpeed (rate-limited)
python scripts/test_pagespeed.py
```

## CI Colors

```css
--fw-purple: #9d4edd;           /* Main brand (primary) */
--fw-purple-light: #c77dff;     /* Hover states */
--fw-purple-dark: #7b2cbf;      /* Depth/shadows */
--fw-tundra: #6b7067;           /* Accent (greenish-grey) */
--fw-tundra-light: #8a8f87;
--fw-tundra-dark: #4a4d45;
```

## Next Agent Tasks

### For Claude (Website)
Continue with:
1. Google PageSpeed test
2. robots.txt + sitemap.xml
3. Image compression (WebP)
4. Accessibility audit (WCAG)

### For Gemini (Radio)
Start with:
1. Check Proxmox/AzuraCast status
2. Get funk.frawo-tech.de online
3. Integrate player on homepage

## Notes
- All content simplified per user feedback ("weniger reden mehr sagen")
- No IT services mentioned (Veranstaltungstechnik only)
- Address: Rothkreuz 14, 88138 Weissensberg
- Wolfgang Prinz: IHK-Fachkraft Veranstaltungstechnik
- Franz Bienert: Zimmermanngeselle
