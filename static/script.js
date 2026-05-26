(function() {
  'use strict';

  /* ══════════════════════════════════════════════════════
     Toast Notification System
     ══════════════════════════════════════════════════════ */
  const toastContainer = document.getElementById('toastContainer');

  function showToast(message, type) {
    if (!toastContainer) return;
    var iconMap = { success: 'fa-check', error: 'fa-times', info: 'fa-info' };
    var icon = iconMap[type] || 'fa-info';
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML =
      '<span class="toast-icon"><i class="fas ' + icon + '"></i></span>' +
      '<span class="toast-message">' + message + '</span>' +
      '<button class="toast-close" aria-label="Dismiss">&times;</button>';
    toast.querySelector('.toast-close').addEventListener('click', function() { removeToast(toast); });
    toastContainer.appendChild(toast);
    setTimeout(function() { removeToast(toast); }, 4500);
  }

  function removeToast(toast) {
    if (toast.classList.contains('removing')) return;
    toast.classList.add('removing');
    setTimeout(function() { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 300);
  }

  // Convert flash messages to toasts
  var flashContainer = document.getElementById('flashData');
  if (flashContainer) {
    flashContainer.querySelectorAll('[data-message]').forEach(function(el) {
      var msg = el.getAttribute('data-message');
      var cat = el.getAttribute('data-category');
      showToast(msg, cat === 'error' ? 'error' : cat === 'success' ? 'success' : 'info');
    });
  }

  /* ══════════════════════════════════════════════════════
     Theme Toggle
     ══════════════════════════════════════════════════════ */
  var themeToggle = document.getElementById('themeToggle');
  var htmlEl = document.documentElement;
  var savedTheme = localStorage.getItem('airbnb-theme') || 'light';

  function setTheme(theme) {
    htmlEl.setAttribute('data-theme', theme);
    localStorage.setItem('airbnb-theme', theme);
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'dark'
        ? '<i class="fas fa-sun"></i>'
        : '<i class="fas fa-moon"></i>';
    }
  }
  setTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      var cur = htmlEl.getAttribute('data-theme');
      setTheme(cur === 'dark' ? 'light' : 'dark');
    });
  }

  /* ══════════════════════════════════════════════════════
     Mobile Nav Toggle
     ══════════════════════════════════════════════════════ */
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function() {
      var isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen);
      navToggle.innerHTML = isOpen
        ? '<i class="fas fa-times"></i>'
        : '<i class="fas fa-bars"></i>';
    });
    // Close on link click
    navLinks.querySelectorAll('.nav-item').forEach(function(link) {
      link.addEventListener('click', function() {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.innerHTML = '<i class="fas fa-bars"></i>';
      });
    });
  }

  /* ══════════════════════════════════════════════════════
     IntersectionObserver — Scroll Reveal
     ══════════════════════════════════════════════════════ */
  var revealObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .scale-in').forEach(function(el) {
    revealObserver.observe(el);
  });

  /* ══════════════════════════════════════════════════════
     Animated Counters
     ══════════════════════════════════════════════════════ */
  var counterObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  function animateCounter(el) {
    var target = parseFloat(el.getAttribute('data-target'));
    if (isNaN(target)) return;
    var suffix = el.getAttribute('data-suffix') || '';
    var prefix = el.getAttribute('data-prefix') || '';
    var duration = 1200;
    var start = performance.now();

    function step(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = eased * target;
      el.textContent = prefix + (target % 1 === 0 ? Math.round(current) : current.toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  document.querySelectorAll('.stat-value[data-target], .hero-stat-value[data-target]').forEach(function(el) {
    counterObserver.observe(el);
  });

  /* ══════════════════════════════════════════════════════
     Hero Canvas — Particle Effect
     ══════════════════════════════════════════════════════ */
  var heroCanvas = document.getElementById('heroCanvas');
  if (heroCanvas) {
    var ctx = heroCanvas.getContext('2d');
    var particles = [];
    var pCount = 60;

    function resizeCanvas() {
      heroCanvas.width = heroCanvas.offsetWidth;
      heroCanvas.height = heroCanvas.offsetHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    for (var i = 0; i < pCount; i++) {
      particles.push({
        x: Math.random() * heroCanvas.width,
        y: Math.random() * heroCanvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1,
        a: Math.random() * 0.5 + 0.1
      });
    }

    function drawParticles() {
      ctx.clearRect(0, 0, heroCanvas.width, heroCanvas.height);
      particles.forEach(function(p) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = heroCanvas.width;
        if (p.x > heroCanvas.width) p.x = 0;
        if (p.y < 0) p.y = heroCanvas.height;
        if (p.y > heroCanvas.height) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,' + p.a + ')';
        ctx.fill();
      });
      // Draw connections
      ctx.strokeStyle = 'rgba(255,255,255,0.04)';
      ctx.lineWidth = 0.5;
      for (var i = 0; i < particles.length; i++) {
        for (var j = i + 1; j < particles.length; j++) {
          var dx = particles[i].x - particles[j].x;
          var dy = particles[i].y - particles[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(drawParticles);
    }
    drawParticles();
  }

  /* ══════════════════════════════════════════════════════
     Live Exchange Rates
     ══════════════════════════════════════════════════════ */
  var liveRates = { USD: 1, EUR: 0.92, GBP: 0.79, INR: 83.0, JPY: 149.0 };

  function fetchRates() {
    var el = document.getElementById('liveRates');
    var ts = document.getElementById('rateTimestamp');
    if (!el) return;
    fetch('https://api.exchangerate-api.com/v4/latest/USD')
      .then(function(r) { return r.json(); })
      .then(function(d) {
        liveRates = { USD: 1, EUR: d.rates.EUR, GBP: d.rates.GBP, INR: d.rates.INR, JPY: d.rates.JPY };
        el.innerHTML = '1 USD = ₹' + d.rates.INR + ' &middot; €' + d.rates.EUR + ' &middot; £' + d.rates.GBP + ' &middot; ¥' + d.rates.JPY;
        if (ts) ts.textContent = 'Updated ' + new Date().toLocaleTimeString();
      })
      .catch(function() {
        el.innerHTML = '1 USD = ₹83 &middot; €0.92 &middot; £0.79 &middot; ¥149 <span style="opacity:0.5;font-size:0.7rem;">(offline)</span>';
      });
  }
  fetchRates();
  setInterval(fetchRates, 300000);

  /* ══════════════════════════════════════════════════════
     Indian City Coordinates
     ══════════════════════════════════════════════════════ */
  var cityCoords = {
    Mumbai: [19.0760, 72.8777],
    Delhi: [28.7041, 77.1025],
    Bangalore: [12.9716, 77.5946],
    Chennai: [13.0827, 80.2707],
    Hyderabad: [17.3850, 78.4867],
    Pune: [18.5204, 73.8567],
    Goa: [15.4909, 73.8278],
    Kolkata: [22.5726, 88.3639],
    Jaipur: [26.9124, 75.7873]
  };

  var citySelect = document.getElementById('citySelect');
  var latInput = document.getElementById('latitude');
  var lngInput = document.getElementById('longitude');

  if (citySelect) {
    citySelect.addEventListener('change', function() {
      var coords = cityCoords[citySelect.value];
      if (coords) {
        latInput.value = coords[0];
        lngInput.value = coords[1];
        updateMap();
      }
    });
  }

  /* ══════════════════════════════════════════════════════
     Range Sliders
     ══════════════════════════════════════════════════════ */
  document.querySelectorAll('input[type="range"]').forEach(function(slider) {
    var display = slider.nextElementSibling;
    if (!display || !display.classList.contains('range-value')) return;
    function update() { display.textContent = slider.value; }
    slider.addEventListener('input', update);
    update();
  });

  /* ══════════════════════════════════════════════════════
     Amenities Checkboxes
     ══════════════════════════════════════════════════════ */
  var amenityCount = document.getElementById('amenityCount');

  function updateAmenityCount() {
    var n = document.querySelectorAll('.amenity-checkbox.selected').length;
    if (amenityCount) amenityCount.textContent = n;
  }

  document.querySelectorAll('.amenity-checkbox').forEach(function(el) {
    el.addEventListener('click', function(e) {
      if (e.target.closest('input')) return;
      var cb = el.querySelector('input[type="checkbox"]');
      cb.checked = !cb.checked;
      el.classList.toggle('selected', cb.checked);
      updateAmenityCount();
    });
    var cb = el.querySelector('input[type="checkbox"]');
    if (cb && cb.checked) el.classList.add('selected');
  });
  updateAmenityCount();

  /* ══════════════════════════════════════════════════════
     Form Validation
     ══════════════════════════════════════════════════════ */
  function validateField(field) {
    var val = field.value.trim();
    var valid = true;
    if (field.hasAttribute('required') && !val) valid = false;
    if (field.type === 'number' && val !== '') {
      var num = parseFloat(val);
      if (field.min && num < parseFloat(field.min)) valid = false;
      if (field.max && num > parseFloat(field.max)) valid = false;
      if (isNaN(num)) valid = false;
    }
    field.classList.toggle('error', !valid);
    return valid;
  }

  document.querySelectorAll('.form-group select, .form-group input:not([type="checkbox"]):not([type="range"])').forEach(function(field) {
    field.addEventListener('blur', function() { validateField(field); });
    field.addEventListener('input', function() {
      if (field.classList.contains('error')) validateField(field);
    });
  });

  /* ══════════════════════════════════════════════════════
     Form Submit
     ══════════════════════════════════════════════════════ */
  var form = document.getElementById('predictionForm');
  if (form) {
    var spinner = document.getElementById('spinner');
    var skeleton = document.getElementById('skeletonLoader');
    var resultCard = document.getElementById('resultCard');

    form.addEventListener('submit', function(e) {
      var allValid = true;
      form.querySelectorAll('.form-group select, .form-group input:not([type="checkbox"]):not([type="range"])').forEach(function(f) {
        if (!validateField(f)) allValid = false;
      });
      if (!allValid) {
        e.preventDefault();
        var firstErr = form.querySelector('.error');
        if (firstErr) firstErr.focus();
        return;
      }
      if (spinner) spinner.classList.add('show');
    });
  }

  /* ══════════════════════════════════════════════════════
     Currency Converter
     ══════════════════════════════════════════════════════ */
  function convertPrice(priceUSD, currency) {
    var rate = liveRates[currency] || 83;
    var symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', JPY: '¥' };
    var sym = symbols[currency] || '₹';
    return sym + (priceUSD * rate).toFixed(2);
  }

  /* ══════════════════════════════════════════════════════
     Result Display
     ══════════════════════════════════════════════════════ */
  var finalResult = document.getElementById('finalResult');
  if (finalResult && finalResult.dataset.price) {
    var price = parseFloat(finalResult.dataset.price);
    if (!isNaN(price)) {
      function updatePrices(currency) {
        finalResult.textContent = convertPrice(price, currency);
        var l = document.getElementById('priceLow');
        var t = document.getElementById('priceTypical');
        var h = document.getElementById('priceHigh');
        if (l) l.textContent = convertPrice(price * 0.8, currency);
        if (t) t.textContent = convertPrice(price, currency);
        if (h) h.textContent = convertPrice(price * 1.2, currency);
      }
      updatePrices('INR');
      if (resultCard) {
        resultCard.classList.add('show');
        setTimeout(function() {
          if (spinner) spinner.classList.remove('show');
          resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 500);
      }

      var currencySelect = document.getElementById('currencySelect');
      if (currencySelect) {
        currencySelect.addEventListener('change', function() {
          updatePrices(this.value);
        });
      }
    }
  }

  /* ══════════════════════════════════════════════════════
     Market Insights Bar Animation
     ══════════════════════════════════════════════════════ */
  var barObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var bar = entry.target;
        var w = bar.getAttribute('data-width');
        if (w) {
          setTimeout(function() { bar.style.width = w; }, 100);
        }
        barObserver.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.insight-bar-fill').forEach(function(bar) {
    var w = bar.style.width;
    bar.style.width = '0%';
    bar.setAttribute('data-width', w);
    barObserver.observe(bar);
  });

  /* ══════════════════════════════════════════════════════
     ROI Calculator
     ══════════════════════════════════════════════════════ */
  var priceUSD = document.getElementById('roiNightly');
  var occupancySlider = document.getElementById('occupancySlider');
  var nightsSlider = document.getElementById('nightsSlider');
  var occupancyDisplay = document.getElementById('occupancyDisplay');
  var nightsDisplay = document.getElementById('nightsDisplay');
  var roiDynamic = document.getElementById('roiDynamic');

  if (priceUSD && occupancySlider && nightsSlider) {
    var basePrice = parseFloat(priceUSD.textContent.replace('$', ''));

    function updateROI() {
      var occ = parseInt(occupancySlider.value, 10);
      var nights = parseInt(nightsSlider.value, 10);
      if (occupancyDisplay) occupancyDisplay.textContent = occ;
      if (nightsDisplay) nightsDisplay.textContent = nights;
      var nightsPerYear = Math.round(365 * occ / 100);
      var annualUSD = basePrice * nightsPerYear;
      var annualINR = annualUSD * 83;
      var monthlyUSD = basePrice * Math.round(30 * occ / 100);

      var nightlyEl = document.getElementById('roiNightly');
      var monthlyEl = document.getElementById('roiMonthly');
      var yearlyEl = document.getElementById('roiYearly');
      var yearlyInrEl = document.getElementById('roiYearlyINR');

      if (nightlyEl) nightlyEl.textContent = '$' + basePrice.toFixed(2);
      if (monthlyEl) monthlyEl.textContent = '$' + monthlyUSD.toFixed(2);
      if (yearlyEl) yearlyEl.textContent = '$' + annualUSD.toFixed(2);
      if (yearlyInrEl) yearlyInrEl.textContent = '₹' + annualINR.toFixed(2);
      if (roiDynamic) {
        roiDynamic.innerHTML =
          '<span style="color:var(--text-secondary);">Estimated annual revenue at ' + occ + '% occupancy: </span>' +
          '<strong style="font-size:var(--text-lg);color:var(--success);">$' + annualUSD.toFixed(2) + '</strong>' +
          '<span style="color:var(--text-secondary);"> (₹' + annualINR.toFixed(2) + ')</span>' +
          '<br><small style="color:var(--text-tertiary);">' + nightsPerYear + ' nights booked per year &middot; ' +
          nights + ' nights per booking</small>';
      }
    }
    occupancySlider.addEventListener('input', updateROI);
    nightsSlider.addEventListener('input', updateROI);
    updateROI();
  }

  /* ══════════════════════════════════════════════════════
     Map (Leaflet)
     ══════════════════════════════════════════════════════ */
  var mapInstance = null, marker = null;

  function initMap() {
    var lat = parseFloat(latInput ? latInput.value : 19.0760) || 19.0760;
    var lng = parseFloat(lngInput ? lngInput.value : 72.8777) || 72.8777;
    if (typeof L === 'undefined') return;
    mapInstance = L.map('map').setView([lat, lng], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18
    }).addTo(mapInstance);
    marker = L.marker([lat, lng], { draggable: true }).addTo(mapInstance);
    marker.on('dragend', function() {
      var pos = marker.getLatLng();
      if (latInput) latInput.value = pos.lat.toFixed(6);
      if (lngInput) lngInput.value = pos.lng.toFixed(6);
    });
  }

  function updateMap() {
    var lat = parseFloat(latInput ? latInput.value : 0);
    var lng = parseFloat(lngInput ? lngInput.value : 0);
    if (!isNaN(lat) && !isNaN(lng) && mapInstance && marker) {
      mapInstance.setView([lat, lng], 11);
      marker.setLatLng([lat, lng]);
    }
  }

  var mapEl = document.getElementById('map');
  if (mapEl) {
    if (typeof L !== 'undefined') {
      initMap();
    } else {
      var checkLeaflet = setInterval(function() {
        if (typeof L !== 'undefined') {
          clearInterval(checkLeaflet);
          initMap();
        }
      }, 200);
    }
    if (latInput) latInput.addEventListener('change', updateMap);
    if (lngInput) lngInput.addEventListener('change', updateMap);
  }

  /* ══════════════════════════════════════════════════════
     Scroll Progress Bar
     ══════════════════════════════════════════════════════ */
  var scrollBar = document.getElementById('scrollProgress');
  if (scrollBar) {
    window.addEventListener('scroll', function() {
      var h = document.documentElement;
      var total = h.scrollHeight - h.clientHeight;
      scrollBar.style.width = (h.scrollTop / total * 100) + '%';
    });
  }

  /* ══════════════════════════════════════════════════════
     Content Reveal on Page Load
     ══════════════════════════════════════════════════════ */
  var mainContent = document.querySelector('.container, .hero-content, .page-header-content');
  if (mainContent) {
    mainContent.classList.add('page-reveal');
  }

})();
