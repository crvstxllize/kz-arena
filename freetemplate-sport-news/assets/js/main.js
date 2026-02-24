/*
  Sport News Template
  Vanilla JavaScript interactions.
  The script is written as small feature modules:
  each block checks if required elements exist before running.
*/

(function () {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const storage = {
    get(key, fallback = null) {
      try {
        const value = localStorage.getItem(key);
        return value === null ? fallback : JSON.parse(value);
      } catch (_err) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (_err) {
        /* Ignore storage errors in restricted browsers. */
      }
    },
    remove(key) {
      try {
        localStorage.removeItem(key);
      } catch (_err) {}
    },
  };

  const state = {
    filters: storage.get("sport-news-filters", {}),
    activePage: 1,
  };

  function createToast({ title = "Info", message = "", variant = "success", timeout = 2500 } = {}) {
    const stack = $("#toast-stack");
    if (!stack) return;

    const toast = document.createElement("div");
    toast.className = `toast toast--${variant}`;
    toast.innerHTML = `
      <div>
        <div class="toast__title">${title}</div>
        <div class="toast__message">${message}</div>
      </div>
      <button type="button" class="icon-btn" aria-label="Close notification" data-toast-close>x</button>
    `;

    const remove = () => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    };

    toast.addEventListener("click", (event) => {
      if (event.target.closest("[data-toast-close]")) remove();
    });

    stack.appendChild(toast);
    window.setTimeout(remove, timeout);
  }

  /* 1) Theme toggle with localStorage persistence. */
  function initThemeToggle() {
    const root = document.documentElement;
    const toggle = $("[data-theme-toggle]");
    const savedTheme = storage.get("sport-news-theme", null);
    const preferredDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (preferredDark ? "dark" : "light");
    root.setAttribute("data-theme", initialTheme);

    if (!toggle) return;
    toggle.setAttribute("aria-checked", String(initialTheme === "light"));
    toggle.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      toggle.setAttribute("aria-checked", String(next === "light"));
      storage.set("sport-news-theme", next);
      createToast({
        title: "Theme",
        message: next === "dark" ? "Dark theme enabled" : "Light theme enabled",
        variant: "success",
        timeout: 1800,
      });
    });
  }

  /* 2) Sticky header style on scroll. */
  function initStickyHeader() {
    const header = $(".site-header");
    if (!header) return;
    const onScroll = () => header.classList.toggle("is-sticky", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* 3) Mobile menu toggle. */
  function initMobileNav() {
    const toggle = $(".nav-toggle");
    const nav = $("#site-nav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
      document.body.classList.toggle("nav-open", !open);
    });

    nav.addEventListener("click", (event) => {
      const link = event.target.closest(".nav__link");
      if (link && !link.hasAttribute("data-dropdown-toggle")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });
  }

  /* 4) Dropdown toggle (desktop hover + mobile click fallback). */
  function initDropdowns() {
    $$("[data-dropdown-toggle]").forEach((btn) => {
      btn.addEventListener("click", (event) => {
        if (window.innerWidth > 900) return;
        event.preventDefault();
        const item = btn.closest(".nav__item");
        if (!item) return;
        const isOpen = item.classList.contains("is-open");
        $$(".nav__item.is-open").forEach((el) => el !== item && el.classList.remove("is-open"));
        item.classList.toggle("is-open", !isOpen);
      });
    });

    document.addEventListener("click", (event) => {
      if (event.target.closest(".nav__item")) return;
      $$(".nav__item.is-open").forEach((el) => el.classList.remove("is-open"));
    });
  }

  /* 5) Breaking ticker auto-rotation + controls. */
  function initTicker() {
    const ticker = $("[data-ticker]");
    if (!ticker) return;
    const track = $(".ticker__track", ticker);
    const items = $$(".ticker__item", ticker);
    const nextBtn = $("[data-ticker-next]", ticker);
    const prevBtn = $("[data-ticker-prev]", ticker);
    if (!track || items.length === 0) return;

    let index = 0;
    let timer = null;

    const update = () => {
      const itemHeight = items[0].offsetHeight || 52;
      track.style.transform = `translateY(-${index * itemHeight}px)`;
    };

    const go = (dir) => {
      index = (index + dir + items.length) % items.length;
      update();
    };

    const start = () => {
      stop();
      timer = window.setInterval(() => go(1), 3500);
    };

    const stop = () => {
      if (timer) window.clearInterval(timer);
      timer = null;
    };

    nextBtn && nextBtn.addEventListener("click", () => { go(1); start(); });
    prevBtn && prevBtn.addEventListener("click", () => { go(-1); start(); });
    ticker.addEventListener("mouseenter", stop);
    ticker.addEventListener("mouseleave", start);
    window.addEventListener("resize", update);

    update();
    start();
  }

  /* 6) Generic modal open/close (search + subscribe). */
  function initModals() {
    const overlay = $("#page-overlay");
    const openers = $$("[data-open-modal]");
    const closers = $$("[data-close-modal]");
    if (!overlay) return;

    const closeAll = () => {
      overlay.classList.remove("is-open");
      $$(".modal.is-open").forEach((modal) => modal.classList.remove("is-open"));
      document.body.classList.remove("modal-open");
    };

    const openModal = (id) => {
      const modal = document.getElementById(id);
      if (!modal) return;
      overlay.classList.add("is-open");
      modal.classList.add("is-open");
      document.body.classList.add("modal-open");
      const focusTarget = $("input, button, [href]", modal);
      if (focusTarget) focusTarget.focus();
    };

    openers.forEach((btn) => {
      btn.addEventListener("click", () => openModal(btn.dataset.openModal));
    });
    closers.forEach((btn) => btn.addEventListener("click", closeAll));
    overlay.addEventListener("click", closeAll);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeAll();
    });
  }

  /* 7) Search modal demo filtering across data cards. */
  function initSearchModal() {
    const input = $("#site-search-input");
    const results = $("#site-search-results");
    if (!input || !results) return;

    const sourceCards = $$("[data-search-item]");
    const source = sourceCards.map((el) => ({
      title: el.dataset.title || el.querySelector("h3,h4")?.textContent?.trim() || "Untitled",
      category: el.dataset.category || "general",
      url: el.dataset.url || "#",
    }));

    const render = (list) => {
      if (list.length === 0) {
        results.innerHTML = `<div class="search-result">No matches found.</div>`;
        return;
      }
      results.innerHTML = list
        .slice(0, 8)
        .map(
          (item) => `
          <a class="search-result" href="${item.url}">
            <div class="badge">${item.category}</div>
            <div style="margin-top:.4rem; font-weight:700;">${item.title}</div>
          </a>
        `
        )
        .join("");
    };

    render(source.slice(0, 5));

    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (!q) {
        render(source.slice(0, 5));
        return;
      }
      const filtered = source.filter((item) => item.title.toLowerCase().includes(q) || item.category.toLowerCase().includes(q));
      render(filtered);
    });
  }

  /* 8) Tabs component. */
  function initTabs() {
    $$("[data-tabs]").forEach((tabsEl) => {
      const buttons = $$("[role='tab']", tabsEl);
      const panels = $$("[role='tabpanel']", tabsEl);
      buttons.forEach((btn) => {
        btn.addEventListener("click", () => {
          const target = btn.getAttribute("aria-controls");
          buttons.forEach((b) => b.setAttribute("aria-selected", String(b === btn)));
          panels.forEach((panel) => {
            panel.hidden = panel.id !== target;
          });
        });
      });
    });
  }

  /* 9) Catalog search filter. */
  function initCatalogSearch() {
    const input = $("[data-card-search]");
    const cards = $$("[data-filter-card]");
    if (!input || cards.length === 0) return;

    const apply = () => {
      const q = input.value.trim().toLowerCase();
      cards.forEach((card) => {
        const hay = [card.dataset.title, card.dataset.category, card.dataset.kind].join(" ").toLowerCase();
        const visible = hay.includes(q);
        card.hidden = !visible;
      });
      updateEmptyState();
    };

    input.addEventListener("input", apply);
  }

  /* 10) Category chips filter. */
  function initChipFilters() {
    const chipGroup = $("[data-chip-group]");
    if (!chipGroup) return;
    const cards = $$("[data-filter-card]");
    const chips = $$("[data-chip]", chipGroup);
    const hiddenInput = $("[data-filter-kind]");

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        chips.forEach((c) => c.classList.remove("is-active"));
        chip.classList.add("is-active");
        const kind = chip.dataset.chip;
        if (hiddenInput) hiddenInput.value = kind;
        cards.forEach((card) => {
          const matches = kind === "all" || card.dataset.kind === kind;
          const qInput = $("[data-card-search]");
          const q = qInput ? qInput.value.trim().toLowerCase() : "";
          const qMatches = [card.dataset.title, card.dataset.category, card.dataset.kind].join(" ").toLowerCase().includes(q);
          card.hidden = !(matches && qMatches);
        });
        updateEmptyState();
        saveFilters();
      });
    });
  }

  /* 11) Sort cards (fake client-side sort). */
  function initCardSort() {
    const select = $("[data-sort-select]");
    const grid = $("[data-sort-grid]");
    if (!select || !grid) return;

    select.addEventListener("change", () => {
      const cards = $$("[data-filter-card]", grid);
      const sortBy = select.value;
      const sorted = [...cards].sort((a, b) => {
        if (sortBy === "popular") return Number(b.dataset.popularity || 0) - Number(a.dataset.popularity || 0);
        if (sortBy === "oldest") return Number(a.dataset.order || 0) - Number(b.dataset.order || 0);
        return Number(b.dataset.order || 0) - Number(a.dataset.order || 0);
      });
      sorted.forEach((card) => grid.appendChild(card));
      saveFilters();
      createToast({ title: "Catalog", message: `Sorted by: ${sortBy}`, variant: "success", timeout: 1400 });
    });
  }

  /* 12) Fake pagination (show/hide pages of cards). */
  function initPagination() {
    const pagination = $("[data-pagination]");
    const cards = $$("[data-filter-card]");
    if (!pagination || cards.length === 0) return;

    const perPage = Number(pagination.dataset.perPage || 6);
    const buttons = $$(".pagination__btn[data-page]", pagination);
    const prev = $("[data-page-prev]", pagination);
    const next = $("[data-page-next]", pagination);

    const visibleCards = () => cards.filter((card) => !card.hidden);

    const render = () => {
      const activeCards = visibleCards();
      const pages = Math.max(1, Math.ceil(activeCards.length / perPage));
      state.activePage = Math.min(state.activePage, pages);

      buttons.forEach((btn) => {
        const page = Number(btn.dataset.page);
        btn.hidden = page > pages;
        btn.classList.toggle("is-active", page === state.activePage);
      });

      activeCards.forEach((card, index) => {
        const page = Math.floor(index / perPage) + 1;
        card.dataset.page = String(page);
        card.style.display = page === state.activePage ? "" : "none";
      });
      cards.filter((card) => card.hidden).forEach((card) => {
        card.style.display = "none";
      });

      if (prev) prev.disabled = state.activePage <= 1;
      if (next) next.disabled = state.activePage >= pages;
    };

    buttons.forEach((btn) => btn.addEventListener("click", () => {
      state.activePage = Number(btn.dataset.page);
      render();
    }));
    prev && prev.addEventListener("click", () => { state.activePage = Math.max(1, state.activePage - 1); render(); });
    next && next.addEventListener("click", () => { state.activePage += 1; render(); });

    document.addEventListener("sportnews:filters-updated", render);
    render();
  }

  /* 13) Empty state for filtered cards. */
  function updateEmptyState() {
    const grid = $("[data-sort-grid]");
    const empty = $("[data-empty-state]");
    if (!grid || !empty) return;
    const anyVisible = $$("[data-filter-card]", grid).some((card) => !card.hidden);
    empty.hidden = anyVisible;
    document.dispatchEvent(new CustomEvent("sportnews:filters-updated"));
  }

  /* 14) Save/restore catalog filters in localStorage. */
  function saveFilters() {
    const searchInput = $("[data-card-search]");
    const sortSelect = $("[data-sort-select]");
    const activeChip = $("[data-chip].is-active");
    storage.set("sport-news-filters", {
      search: searchInput ? searchInput.value : "",
      sort: sortSelect ? sortSelect.value : "newest",
      chip: activeChip ? activeChip.dataset.chip : "all",
    });
  }

  function restoreFilters() {
    const config = storage.get("sport-news-filters", null);
    if (!config) return;
    const searchInput = $("[data-card-search]");
    const sortSelect = $("[data-sort-select]");
    const chips = $$("[data-chip]");

    if (searchInput && typeof config.search === "string") {
      searchInput.value = config.search;
      searchInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (sortSelect && typeof config.sort === "string") {
      sortSelect.value = config.sort;
      sortSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (config.chip && chips.length) {
      const chip = chips.find((c) => c.dataset.chip === config.chip);
      chip && chip.click();
    }
  }

  /* 15) Match status filter. */
  function initMatchFilter() {
    const buttons = $$("[data-match-filter]");
    const rows = $$("[data-match-row]");
    if (buttons.length === 0 || rows.length === 0) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        const status = btn.dataset.matchFilter;
        rows.forEach((row) => {
          row.hidden = !(status === "all" || row.dataset.status === status);
        });
      });
    });
  }

  /* 16) Accordion FAQ. */
  function initAccordion() {
    $$("[data-accordion]").forEach((accordion) => {
      accordion.addEventListener("click", (event) => {
        const btn = event.target.closest("[data-accordion-btn]");
        if (!btn) return;
        const item = btn.closest(".accordion__item");
        const panel = item && $(".accordion__panel", item);
        if (!item || !panel) return;
        const open = item.classList.contains("is-open");

        $$(".accordion__item", accordion).forEach((other) => {
          other.classList.remove("is-open");
          const p = $(".accordion__panel", other);
          if (p) p.style.maxHeight = "0px";
          const b = $("[data-accordion-btn]", other);
          if (b) b.setAttribute("aria-expanded", "false");
        });

        if (!open) {
          item.classList.add("is-open");
          btn.setAttribute("aria-expanded", "true");
          panel.style.maxHeight = panel.scrollHeight + "px";
        }
      });
    });
  }

  /* 17) Copy article link button. */
  function initCopyLink() {
    const btn = $("[data-copy-link]");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const url = btn.dataset.url || window.location.href;
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(url);
        } else {
          const tmp = document.createElement("input");
          tmp.value = url;
          document.body.appendChild(tmp);
          tmp.select();
          document.execCommand("copy");
          tmp.remove();
        }
        createToast({ title: "Link copied", message: "Article URL copied to clipboard.", variant: "success" });
      } catch (_err) {
        createToast({ title: "Copy failed", message: "Browser blocked clipboard access.", variant: "error" });
      }
    });
  }

  /* 18) Expand/collapse long article text. */
  function initArticleCollapse() {
    const btn = $("[data-toggle-article]");
    const content = $("[data-article-content]");
    if (!btn || !content) return;
    btn.addEventListener("click", () => {
      const collapsed = content.getAttribute("data-collapsed") === "true";
      content.setAttribute("data-collapsed", String(!collapsed));
      btn.textContent = collapsed ? "Collapse text" : "Read more";
    });
  }

  /* 19) Password visibility toggle. */
  function initPasswordToggle() {
    $$("[data-password-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = document.getElementById(btn.dataset.passwordToggle);
        if (!target) return;
        const hidden = target.type === "password";
        target.type = hidden ? "text" : "password";
        btn.setAttribute("aria-pressed", String(hidden));
      });
    });
  }

  /* 20) Password strength meter (register page). */
  function initPasswordStrength() {
    const input = $("#register-password");
    const fill = $("[data-strength-fill]");
    const text = $("[data-strength-text]");
    if (!input || !fill || !text) return;

    const scorePassword = (value) => {
      let score = 0;
      if (value.length >= 8) score++;
      if (/[A-Z]/.test(value)) score++;
      if (/[a-z]/.test(value) && /\d/.test(value)) score++;
      if (/[^A-Za-z0-9]/.test(value)) score++;
      return Math.min(score, 4);
    };

    input.addEventListener("input", () => {
      const score = scorePassword(input.value);
      const pct = (score / 4) * 100;
      fill.style.width = pct + "%";
      const labels = ["Too weak", "Weak", "Fair", "Good", "Strong"];
      text.textContent = `Password strength: ${labels[score]}`;
    });
  }

  /* 21) Register form validation (confirm password + terms). */
  function initRegisterValidation() {
    const form = $("#register-form");
    if (!form) return;
    const password = $("#register-password", form);
    const confirm = $("#register-password-confirm", form);
    const terms = $("#register-terms", form);
    const error = $("#register-error", form);

    form.addEventListener("submit", (event) => {
      let message = "";
      if (!password.value || password.value.length < 8) {
        message = "Password must contain at least 8 characters.";
      } else if (password.value !== confirm.value) {
        message = "Passwords do not match.";
      } else if (!terms.checked) {
        message = "Please accept the terms to continue.";
      }

      if (message) {
        event.preventDefault();
        if (error) {
          error.hidden = false;
          error.textContent = message;
        }
        createToast({ title: "Register form", message, variant: "error" });
      } else {
        event.preventDefault();
        if (error) error.hidden = true;
        createToast({ title: "Demo form", message: "Registration is a front-end demo only.", variant: "success" });
      }
    });
  }

  /* 22) Login form validation (basic required checks). */
  function initLoginValidation() {
    const form = $("#login-form");
    if (!form) return;
    const email = $("#login-email", form);
    const password = $("#login-password", form);
    const error = $("#login-error", form);

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const emailValid = /^\S+@\S+\.\S+$/.test(email.value);
      if (!emailValid || password.value.length < 6) {
        if (error) {
          error.hidden = false;
          error.textContent = "Enter a valid email and password (min 6 chars).";
        }
        createToast({ title: "Login form", message: "Validation failed.", variant: "error" });
        return;
      }
      if (error) error.hidden = true;
      createToast({ title: "Demo login", message: "Success (demo only, no backend).", variant: "success" });
    });
  }

  /* 23) Bookmark toggle on cards. */
  function initBookmarks() {
    $$("[data-bookmark-btn]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const active = btn.classList.toggle("is-active");
        btn.setAttribute("aria-pressed", String(active));
        createToast({
          title: active ? "Saved" : "Removed",
          message: active ? "Article added to bookmarks." : "Article removed from bookmarks.",
          variant: "success",
          timeout: 1500,
        });
      });
    });
  }

  /* 24) Like buttons with local counter increment. */
  function initLikeButtons() {
    $$("[data-like-btn]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const liked = btn.classList.toggle("is-active");
        const countNode = $("[data-like-count]", btn);
        if (countNode) {
          const current = Number(countNode.textContent || 0);
          countNode.textContent = String(current + (liked ? 1 : -1));
        }
      });
    });
  }

  /* 25) Fake pagination "load more" / skeleton demo toggle. */
  function initDemoButtons() {
    const skeletonBtn = $("[data-toggle-skeleton]");
    const skeletonBox = $("[data-skeleton-demo]");
    if (skeletonBtn && skeletonBox) {
      skeletonBtn.addEventListener("click", () => {
        const visible = skeletonBox.classList.toggle("is-visible");
        skeletonBtn.textContent = visible ? "Hide skeleton demo" : "Show skeleton demo";
      });
    }

    $$("[data-toast-demo]").forEach((btn) => {
      btn.addEventListener("click", () => {
        createToast({ title: "Demo action", message: btn.dataset.toastDemo || "Action triggered.", variant: "success" });
      });
    });
  }

  /* 26) Dismissible alerts. */
  function initAlerts() {
    $$("[data-alert-close]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const alert = btn.closest(".alert");
        alert && alert.remove();
      });
    });
  }

  /* 27) Back-to-top button visibility + action. */
  function initBackToTop() {
    const btn = $("#back-to-top");
    if (!btn) return;
    const onScroll = () => btn.classList.toggle("is-visible", window.scrollY > 300);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  function initPageSignals() {
    /* Useful hook for pages that want to show local page context. */
    const pageName = document.body.dataset.page;
    if (pageName) {
      document.body.classList.add(`page-${pageName}`);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initStickyHeader();
    initMobileNav();
    initDropdowns();
    initTicker();
    initModals();
    initSearchModal();
    initTabs();
    initCatalogSearch();
    initChipFilters();
    initCardSort();
    initPagination();
    initMatchFilter();
    initAccordion();
    initCopyLink();
    initArticleCollapse();
    initPasswordToggle();
    initPasswordStrength();
    initRegisterValidation();
    initLoginValidation();
    initBookmarks();
    initLikeButtons();
    initDemoButtons();
    initAlerts();
    initBackToTop();
    initPageSignals();
    restoreFilters();
    updateEmptyState();
  });
})();
