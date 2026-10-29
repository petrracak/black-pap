/* BLACK PAP | Método PAP · Fernanda Garnizet */
(function () {
  "use strict";

  /* ================== CONFIGURAÇÃO ==================
     Troque os links aqui: todos os botões de compra usam CHECKOUT_URL
     e o botão "Tirar uma dúvida" usa WHATSAPP_URL. */
  var CHECKOUT_URL = "https://pay.hotmart.com/U108012639R?off=gi2yx3uq&checkoutMode=10";
  var WHATSAPP_URL = "";   // ex.: "https://wa.me/5511999999999?text=Oi!%20Tenho%20uma%20d%C3%BAvida%20sobre%20a%20Black%20PAP"
  /* ================================================== */

  var doc = document.documentElement;
  var body = document.body;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover)").matches;
  body.classList.add("bp-js");

  function clamp(v, a, b) { return Math.max(a === undefined ? 0 : a, Math.min(b === undefined ? 1 : b, v)); }
  function ease(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function debounce(fn, ms) { var t; return function () { clearTimeout(t); t = setTimeout(fn, ms || 150); }; }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* ---------- links ---------- */
  $all("[data-checkout]").forEach(function (a) {
    if (CHECKOUT_URL) a.href = CHECKOUT_URL;
    else if (a.getAttribute("href") === "#") a.href = "#oferta";
  });
  if (WHATSAPP_URL) $all("[data-whatsapp]").forEach(function (a) { a.href = WHATSAPP_URL; });
  // Reposiciona após o navegador calcular as seções que estavam fora da tela.
  $all('a[href="#valor"]').forEach(function (a) {
    a.addEventListener("click", function (event) {
      var target = document.getElementById("valor");
      if (!target) return;
      event.preventDefault();
      history.pushState(null, "", "#valor");
      target.scrollIntoView({ behavior: "instant", block: "start" });
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { target.scrollIntoView({ behavior: "instant", block: "start" }); });
      });
    });
  });

  /* ---------- entrada da primeira dobra ---------- */
  requestAnimationFrame(function () { body.classList.add("bp-ready"); });

  /* ---------- faixas em loop infinito ----------
     Duplica o grupo até cobrir a tela e anda exatamente a largura de um grupo,
     então a emenda nunca aparece, em qualquer largura de tela. */
  function setupMarquee(track) {
    var group = track.querySelector(".bp-band__group");
    var speed = track.getAttribute("data-marquee") === "slow" ? 28 : 64; // px por segundo
    function fill() {
      $all(".is-clone", track).forEach(function (c) { c.remove(); });
      var w = group.getBoundingClientRect().width;
      if (!w) return;
      var copies = Math.ceil(window.innerWidth * 1.3 / w) + 1;
      for (var i = 0; i < copies; i++) {
        var c = group.cloneNode(true);
        c.classList.add("is-clone");
        track.appendChild(c);
      }
      track.style.setProperty("--shift", w + "px");
      track.style.setProperty("--dur", (w / speed).toFixed(2) + "s");
    }
    fill();
    window.addEventListener("resize", debounce(fill));
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fill);
  }
  $all("[data-marquee]").forEach(setupMarquee);

  /* ---------- revelar no scroll ----------
     [data-reveal]: o bloco inteiro entra de uma vez.
     [data-stagger]: cada filho entra quando chega na tela, em cascata com os vizinhos. */
  var revealEls = $all("[data-reveal]");
  var staggerEls = [];
  $all("[data-stagger]").forEach(function (list) {
    Array.prototype.forEach.call(list.children, function (el) { staggerEls.push(el); });
  });
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      var batch = entries.filter(function (e) { return e.isIntersecting; }).map(function (e) { return e.target; });
      batch.sort(function (a, b) { return a.compareDocumentPosition(b) & 4 ? -1 : 1; });
      batch.forEach(function (el, k) {
        io.unobserve(el);
        if (el.parentElement && el.parentElement.hasAttribute("data-stagger")) {
          el.style.transitionDelay = (k * 80) + "ms";
          setTimeout(function () { el.style.transitionDelay = ""; }, 900 + k * 80);
        }
        el.classList.add("is-in");
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.concat(staggerEls).forEach(function (el) { io.observe(el); });
  } else {
    revealEls.concat(staggerEls).forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- luz que segue o mouse nos cards ---------- */
  if (finePointer) {
    $all("[data-spot]").forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    });
  }

  /* ---------- cena do PAP: iniciais que se abrem no nome completo ---------- */
  var pap = document.querySelector("[data-pap]");
  var papGeo = null;
  if (pap) {
    var stage = pap.querySelector(".bp-pap__stage");
    var inis = $all(".bp-pap__ini", pap);
    var rest = $all(".bp-pap__r", pap);
    var papLabel = pap.querySelector(".bp-pap__label");
    var papHint = pap.querySelector(".bp-pap__scroll");

    var measurePap = function () {
      inis.forEach(function (el) { el.style.transform = "none"; });
      var s = stage.getBoundingClientRect();
      var rects = inis.map(function (el) { return el.getBoundingClientRect(); });
      var sumW = rects.reduce(function (a, r) { return a + r.width; }, 0);
      var S = clamp(s.width * .78 / sumW, 1.6, 3.1);
      var widths = rects.map(function (r) { return r.width * S * .96; });
      var total = widths.reduce(function (a, b) { return a + b; }, 0);
      var x = s.left + s.width / 2 - total / 2;
      var cy = s.top + s.height / 2;
      papGeo = rects.map(function (r, i) {
        var cx = x + widths[i] / 2;
        x += widths[i];
        return { dx: cx - (r.left + r.width / 2), dy: cy - (r.top + r.height / 2) };
      });
      papGeo.S = S;
      var half = rects[0].height * S / 2;
      papLabel.style.setProperty("--ly", (-half - 26) + "px");
      papHint.style.setProperty("--sy", (half + 18) + "px");
    };

    var renderPap = function (p) {
      if (!papGeo) return;
      var t = ease(clamp((p - .1) / .45));
      var k = 1 - t;
      inis.forEach(function (el, i) {
        var g = papGeo[i];
        el.style.transform = "translate(" + (g.dx * k).toFixed(1) + "px," + (g.dy * k).toFixed(1) + "px) scale(" + (1 + (papGeo.S - 1) * k).toFixed(3) + ")";
      });
      rest.forEach(function (el, j) {
        var start = .32 + j / rest.length * .38;
        var o = clamp((p - start) / .14);
        el.style.opacity = o.toFixed(3);
        el.style.transform = "translateY(" + ((1 - o) * .35).toFixed(3) + "em)";
        el.style.filter = o < 1 ? "blur(" + ((1 - o) * 8).toFixed(1) + "px)" : "none";
      });
      papLabel.style.opacity = (1 - clamp((p - .06) / .14)).toFixed(3);
      papHint.style.opacity = (1 - clamp(p / .07)).toFixed(3);
      stage.style.setProperty("--p", p.toFixed(3));
    };

    if (reduce) {
      pap.classList.add("is-static");
    } else {
      measurePap();
      window.addEventListener("resize", debounce(function () { measurePap(); onScroll(); }));
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measurePap(); onScroll(); });
    }
  }

  /* ---------- cards do "Imagine" empilhando ---------- */
  var scards = $all(".bp-scard");
  scards.forEach(function (c, i) { c.style.setProperty("--i", i); });
  function renderStack() {
    for (var i = 0; i < scards.length - 1; i++) {
      var r = scards[i].getBoundingClientRect();
      var n = scards[i + 1].getBoundingClientRect();
      var cover = clamp((r.bottom - n.top) / r.height);
      scards[i].style.setProperty("--s", (1 - cover * .06).toFixed(4));
      scards[i].style.setProperty("--dim", (cover * .55).toFixed(3));
    }
  }

  /* ---------- scroll: progresso, barra fixa, PAP e pilha ---------- */
  var bar = document.querySelector(".bp-progress span");
  var sticky = document.querySelector(".bp-sticky");
  var hero = document.querySelector(".bp-hero");
  var oferta = document.getElementById("oferta");
  var ticking = false;

  function onScroll() {
    ticking = false;
    var y = window.scrollY;
    var vh = window.innerHeight;
    var max = doc.scrollHeight - vh;
    if (bar) bar.style.transform = "scaleX(" + (max > 0 ? y / max : 0) + ")";
    if (sticky && hero) {
      var past = y > hero.offsetHeight * .8;
      var r = oferta ? oferta.getBoundingClientRect() : null;
      var atOffer = r && r.top < vh && r.bottom > 0;
      sticky.classList.toggle("is-on", past && !atOffer);
    }
    if (pap && papGeo && !reduce) {
      var pr = pap.getBoundingClientRect();
      if (pr.top < vh && pr.bottom > 0) renderPap(clamp(-pr.top / (pr.height - vh)));
    }
    if (scards.length && !reduce) renderStack();
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  onScroll();

  /* ---------- carrosséis ---------- */
  $all("[data-rail]").forEach(function (rail) {
    var track = rail.querySelector(".bp-rail__track");
    var items = Array.prototype.slice.call(track.children);
    var prev = rail.querySelector(".bp-rail__arrow--prev");
    var next = rail.querySelector(".bp-rail__arrow--next");
    var now = rail.querySelector("[data-rail-now]");
    var total = rail.querySelector("[data-rail-total]");
    var current = -1;
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    if (total) total.textContent = pad(items.length);

    function center(el) { return el.offsetLeft + el.offsetWidth / 2; }

    function update() {
      var mid = track.scrollLeft + track.clientWidth / 2;
      var best = 0, dist = Infinity;
      items.forEach(function (el, i) {
        var off = center(el) - mid;
        var d = clamp(off / (el.offsetWidth || 1), -2, 2);
        el.style.setProperty("--d", d.toFixed(3));
        el.style.setProperty("--ad", Math.min(Math.abs(d), 1.5).toFixed(3));
        if (Math.abs(off) < dist) { dist = Math.abs(off); best = i; }
      });
      if (best !== current) {
        if (items[current]) items[current].classList.remove("is-focus");
        items[best].classList.add("is-focus");
        current = best;
        if (now) now.textContent = pad(current + 1);
      }
      if (prev) prev.disabled = current <= 0;
      if (next) next.disabled = current >= items.length - 1;
    }

    function go(i) {
      i = clamp(i, 0, items.length - 1);
      track.scrollTo({ left: center(items[i]) - track.clientWidth / 2, behavior: reduce ? "auto" : "smooth" });
    }

    if (prev) prev.addEventListener("click", function () { go(current - 1); });
    if (next) next.addEventListener("click", function () { go(current + 1); });

    var raf = 0;
    track.addEventListener("scroll", function () {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(update);
    }, { passive: true });
    window.addEventListener("resize", debounce(update, 80));

    // tocar num card lateral leva ele para o centro antes de abrir
    track.addEventListener("click", function (e) {
      var item = e.target.closest(".bp-rail__track > *");
      if (!item) return;
      var i = items.indexOf(item);
      if (i !== current) { e.preventDefault(); e.stopPropagation(); go(i); }
    }, true);

    // arrastar com o mouse no computador
    var down = false, startX = 0, startLeft = 0, moved = false;
    track.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse") return;
      down = true; moved = false; startX = e.clientX; startLeft = track.scrollLeft;
      track.style.scrollSnapType = "none";
      track.style.cursor = "grabbing";
    });
    window.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      if (Math.abs(dx) > 4) moved = true;
      track.scrollLeft = startLeft - dx;
    });
    window.addEventListener("pointerup", function () {
      if (!down) return;
      down = false;
      track.style.scrollSnapType = "";
      track.style.cursor = "";
      if (moved) go(current);
    });
    track.addEventListener("click", function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
    }, true);
    track.addEventListener("dragstart", function (e) { e.preventDefault(); });

    // prints muito altos ganham um degradê no fim (os curtos aparecem inteiros)
    $all(".bp-print", track).forEach(function (fig) {
      var btn = fig.querySelector("button");
      var img = fig.querySelector("img");
      var check = function () { fig.classList.toggle("is-cut", img.offsetHeight > btn.clientHeight + 2); };
      if (img.complete) check(); else img.addEventListener("load", check);
      window.addEventListener("resize", debounce(check));
    });

    // começa no segundo card para já ter cards dos dois lados
    var first = items.length > 2 && !rail.classList.contains("bp-rail--metodo") ? 1 : 0;
    requestAnimationFrame(function () {
      track.scrollLeft = center(items[first]) - track.clientWidth / 2;
      update();
    });
  });

  /* ---------- vídeos do YouTube ---------- */
  $all(".bp-video").forEach(function (v) {
    var id = (v.getAttribute("data-youtube") || "").trim();
    if (!id) return;
    v.classList.add("has-video");
    v.style.backgroundImage = "url(https://i.ytimg.com/vi/" + encodeURIComponent(id) + "/hqdefault.jpg)";
  });

  /* ---------- modal (print ampliado e vídeo) ---------- */
  var modal = document.querySelector(".bp-modal");
  var modalBody = modal.querySelector(".bp-modal__body");
  var lastFocus = null;

  function open(html, isVideo) {
    lastFocus = document.activeElement;
    modalBody.innerHTML = html;
    modalBody.classList.toggle("is-video", !!isVideo);
    modal.hidden = false;
    body.style.overflow = "hidden";
    modal.querySelector(".bp-modal__close").focus();
  }
  function close() {
    modal.hidden = true;
    modalBody.innerHTML = "";
    body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  modal.querySelector(".bp-modal__close").addEventListener("click", close);
  modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !modal.hidden) close(); });

  $all("[data-zoom]").forEach(function (b) {
    b.addEventListener("click", function () {
      var img = b.querySelector("img");
      open('<img src="' + b.getAttribute("data-zoom") + '" alt="' + (img ? img.alt.replace(/"/g, "&quot;") : "") + '">');
    });
  });
  $all(".bp-video").forEach(function (v) {
    v.addEventListener("click", function () {
      var id = (v.getAttribute("data-youtube") || "").trim();
      if (!id) return;
      open('<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0&playsinline=1" title="Depoimento em vídeo" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>', true);
    });
  });

  /* ---------- selo de garantia: traços em volta ---------- */
  var NS = "http://www.w3.org/2000/svg";
  function ticks(g, r1, r2, step, width, opacity) {
    for (var a = 0; a < 360; a += step) {
      var op = opacity(a);
      if (op <= 0) continue;
      var rad = (a - 90) * Math.PI / 180;
      var l = document.createElementNS(NS, "line");
      l.setAttribute("x1", (200 + r1 * Math.cos(rad)).toFixed(2));
      l.setAttribute("y1", (200 + r1 * Math.sin(rad)).toFixed(2));
      l.setAttribute("x2", (200 + r2 * Math.cos(rad)).toFixed(2));
      l.setAttribute("y2", (200 + r2 * Math.sin(rad)).toFixed(2));
      l.setAttribute("stroke", "#e6c27a");
      l.setAttribute("stroke-width", width);
      l.setAttribute("stroke-linecap", "round");
      l.setAttribute("stroke-opacity", op.toFixed(2));
      g.appendChild(l);
    }
  }
  var outer = document.querySelector('[data-ticks="outer"]');
  var inner = document.querySelector('[data-ticks="inner"]');
  // dois arcos (esquerda e direita) que somem perto do topo e da base, como no arquivo do Figma
  if (outer) ticks(outer, 170, 186, 3.6, 2.2, function (a) { return clamp((Math.abs(Math.sin(a * Math.PI / 180)) - .2) / .55) * .9; });
  if (inner) ticks(inner, 56, 66, 9, 2, function () { return .75; });

  /* ---------- preço caindo de 2.997 para 997 ---------- */
  var priceEl = document.querySelector("[data-count-from]");
  if (priceEl && "IntersectionObserver" in window && !reduce) {
    var from = +priceEl.getAttribute("data-count-from");
    var to = +priceEl.getAttribute("data-count-to");
    var fmt = function (n) { return Math.round(n).toLocaleString("pt-BR"); };
    priceEl.textContent = fmt(from);
    var po = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      po.disconnect();
      var t0 = performance.now(), dur = 1500;
      (function step(t) {
        var k = Math.min(1, (t - t0) / dur);
        priceEl.textContent = fmt(from + (to - from) * (1 - Math.pow(1 - k, 4)));
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    }, { threshold: .6 });
    po.observe(priceEl);
  }
})();
