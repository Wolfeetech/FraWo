/* FraWo CI 3.0 — Frontend-Interaktionen
   Lesefortschritts-Balken und Einblenden von Abschnitten beim Scrollen.
   Wird gebündelt geladen, deshalb darf nicht blind auf DOMContentLoaded
   gewartet werden: das Ereignis kann bereits vorbei sein. */

(function () {
    "use strict";

    function initScrollProgress() {
        var bar = document.getElementById("fw-scroll-progress");
        if (!bar) {
            bar = document.createElement("div");
            bar.id = "fw-scroll-progress";
            document.body.appendChild(bar);
        }

        var ticking = false;
        function update() {
            var doc = document.documentElement;
            var height = doc.scrollHeight - doc.clientHeight;
            var scrolled = height > 0 ? (doc.scrollTop / height) * 100 : 0;
            bar.style.width = scrolled + "%";
            ticking = false;
        }

        window.addEventListener("scroll", function () {
            if (!ticking) {
                ticking = true;
                window.requestAnimationFrame(update);
            }
        }, { passive: true });

        update();
    }

    function initReveals() {
        var targets = document.querySelectorAll(".fw-reveal, .fw-reveal-scale");
        if (!targets.length) {
            return;
        }

        // Ohne IntersectionObserver alles sofort sichtbar machen,
        // damit Inhalte nie unsichtbar hängen bleiben.
        if (!("IntersectionObserver" in window)) {
            targets.forEach(function (el) {
                el.classList.add("fw-reveal-active");
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("fw-reveal-active");
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        targets.forEach(function (el) {
            observer.observe(el);
        });
    }

    function init() {
        initScrollProgress();
        initReveals();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
