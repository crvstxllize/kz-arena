function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (const cookie of cookies) {
    const [key, ...rest] = cookie.trim().split("=");
    if (key === name) {
      return decodeURIComponent(rest.join("="));
    }
  }
  return null;
}

function showToast(text, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) {
    return;
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.setAttribute("role", "status");
  toast.textContent = text;
  container.appendChild(toast);

  window.setTimeout(() => {
    toast.remove();
  }, 2800);
}

async function fetchJSON(url, options = {}) {
  const csrfToken = getCookie("csrftoken");
  const headers = {
    "X-Requested-With": "XMLHttpRequest",
    ...(options.headers || {}),
  };

  if (options.method && options.method.toUpperCase() !== "GET") {
    headers["X-CSRFToken"] = csrfToken || "";
    if (!headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
  }

  const response = await fetch(url, { ...options, headers });
  let payload = null;

  try {
    payload = await response.json();
  } catch (_error) {
    payload = null;
  }

  if (response.status === 401) {
    const loginUrl = document.querySelector("[data-login-url]")?.dataset.loginUrl;
    showToast("Войдите, чтобы выполнить действие", "error");
    if (loginUrl) {
      window.setTimeout(() => {
        window.location.href = loginUrl;
      }, 700);
    }
    throw new Error("auth_required");
  }

  if (!response.ok || !payload || payload.ok === false) {
    const message = payload?.error || "Ошибка запроса";
    showToast(message, "error");
    throw new Error(message);
  }

  return payload;
}

function initMobileMenu() {
  const navToggle = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");
  if (!navToggle || !navMenu) {
    return;
  }

  const closeMenu = () => {
    navMenu.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  };

  navToggle.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navMenu.querySelectorAll("a, button").forEach((link) => {
    link.addEventListener("click", () => {
      closeMenu();
    });
  });

  document.addEventListener("click", (event) => {
    if (!navMenu.classList.contains("is-open")) {
      return;
    }
    if (navMenu.contains(event.target) || navToggle.contains(event.target)) {
      return;
    }
    closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && navMenu.classList.contains("is-open")) {
      closeMenu();
      navToggle.focus();
    }
  });
}

function initBackToTop() {
  const backToTopBtn = document.getElementById("back-to-top");
  if (!backToTopBtn) {
    return;
  }

  const updateBackToTop = () => {
    if (window.scrollY > 280) {
      backToTopBtn.classList.add("is-visible");
    } else {
      backToTopBtn.classList.remove("is-visible");
    }
  };

  window.addEventListener("scroll", updateBackToTop, { passive: true });
  updateBackToTop();

  backToTopBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

function initStickyHeader() {
  const header = document.getElementById("site-header");
  if (!header) {
    return;
  }

  const onScroll = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 20);
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function initThemeToggle() {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) {
    return;
  }

  const root = document.documentElement;
  const storageKey = "theme";
  const media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: light)") : null;

  const resolveTheme = () => {
    const stored = window.localStorage.getItem(storageKey);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
    if (media && media.matches) {
      return "light";
    }
    return "dark";
  };

  const applyTheme = (theme, persist) => {
    root.dataset.theme = theme;
    toggle.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
    toggle.setAttribute("aria-label", theme === "dark" ? "Переключить на светлую тему" : "Переключить на тёмную тему");
    if (persist) {
      window.localStorage.setItem(storageKey, theme);
    }
  };

  applyTheme(resolveTheme(), false);

  toggle.addEventListener("click", () => {
    const isDark = root.dataset.theme === "dark";
    if (isDark) {
      applyTheme("light", true);
      showToast("Светлая тема включена", "info");
    } else {
      applyTheme("dark", true);
      showToast("Темная тема включена", "info");
    }
  });

  if (media && typeof media.addEventListener === "function") {
    media.addEventListener("change", () => {
      const stored = window.localStorage.getItem(storageKey);
      if (stored === "light" || stored === "dark") {
        return;
      }
      applyTheme(media.matches ? "light" : "dark", false);
    });
  }
}

function initNewsStripScroll() {
  const strip = document.querySelector("[data-news-strip]");
  const prev = document.querySelector("[data-strip-prev]");
  const next = document.querySelector("[data-strip-next]");
  if (!strip || !prev || !next) {
    return;
  }

  const shift = () => Math.max(260, Math.min(420, Math.round(strip.clientWidth * 0.8)));

  prev.addEventListener("click", () => {
    strip.scrollBy({ left: -shift(), behavior: "smooth" });
  });

  next.addEventListener("click", () => {
    strip.scrollBy({ left: shift(), behavior: "smooth" });
  });
}

function initSmoothAnchors() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      const targetId = anchor.getAttribute("href");
      if (!targetId || targetId === "#") {
        return;
      }
      const target = document.querySelector(targetId);
      if (!target) {
        return;
      }
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function initAutocomplete() {
  const root = document.querySelector("[data-autocomplete-root]");
  const input = document.querySelector("[data-autocomplete-input]");
  const list = document.querySelector("[data-autocomplete-list]");
  if (!root || !input || !list) {
    return;
  }

  let timer = null;

  const close = () => {
    list.innerHTML = "";
    list.hidden = true;
  };

  const render = (items) => {
    if (!items.length) {
      close();
      return;
    }

    list.innerHTML = items
      .map(
        (item) =>
          `<a class="search-autocomplete__item" href="${item.url}"><span>${item.title}</span></a>`,
      )
      .join("");
    list.hidden = false;
  };

  input.addEventListener("input", () => {
    const query = input.value.trim();
    if (timer) {
      window.clearTimeout(timer);
    }

    if (query.length < 2) {
      close();
      return;
    }

    timer = window.setTimeout(async () => {
      try {
        const searchUrl = new URL(input.dataset.searchUrl, window.location.origin);
        searchUrl.searchParams.set("q", query);
        const payload = await fetchJSON(searchUrl.toString(), { method: "GET" });
        render(payload.data?.results || []);
      } catch (_error) {
        close();
      }
    }, 300);
  });

  document.addEventListener("click", (event) => {
    if (!root.contains(event.target)) {
      close();
    }
  });
}

function initLoadMore() {
  const button = document.querySelector("[data-load-more]");
  const grid = document.getElementById("news-grid");
  const pagination = document.querySelector("[data-pagination]");
  if (!button || !grid || !pagination) {
    return;
  }

  button.addEventListener("click", async () => {
    const nextUrl = button.dataset.nextUrl;
    if (!nextUrl) {
      return;
    }

    button.disabled = true;
    button.textContent = "Загрузка...";

    try {
      const response = await fetch(nextUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      const html = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");

      const incomingCards = doc.querySelectorAll("#news-grid .news-card");
      incomingCards.forEach((card) => {
        grid.appendChild(card);
      });

      const nextLink = doc.querySelector("[data-next-page]");
      if (nextLink) {
        button.dataset.nextUrl = nextLink.getAttribute("href") || "";
        button.disabled = false;
        button.textContent = "Показать ещё";
      } else {
        button.remove();
      }

      const currentLabel = pagination.querySelector(".pagination-current");
      const newLabel = doc.querySelector(".pagination-current");
      if (currentLabel && newLabel) {
        currentLabel.textContent = newLabel.textContent;
      }
    } catch (_error) {
      showToast("Не удалось подгрузить новости", "error");
      button.disabled = false;
      button.textContent = "Показать ещё";
    }
  });
}

function initNewsDetailInteractions() {
  const detail = document.querySelector(".news-detail[data-article-id]");
  if (!detail) {
    return;
  }

  const articleId = Number(detail.dataset.articleId);
  const isAuthenticated = detail.dataset.authenticated === "1";
  const reactUrl = detail.dataset.reactUrl;
  const favoriteUrl = detail.dataset.favoriteUrl;
  const subscribeUrl = detail.dataset.subscribeUrl;
  const rateUrl = detail.dataset.rateUrl;
  const statusUrl = detail.dataset.statusUrl;

  const likeCountEl = detail.querySelector("[data-like-count]");
  const dislikeCountEl = detail.querySelector("[data-dislike-count]");
  const favoriteCountEl = detail.querySelector("[data-favorite-count]");
  const ratingAverageEl = detail.querySelector("[data-rating-average]");
  const ratingCountEl = detail.querySelector("[data-rating-count]");

  const reactButtons = detail.querySelectorAll(".js-react-btn");
  const favoriteBtn = detail.querySelector(".js-favorite-btn");
  const subscribeBtn = detail.querySelector(".js-subscribe-btn");
  const rateButtons = detail.querySelectorAll(".js-rate-btn");

  const setReactionState = (type) => {
    reactButtons.forEach((btn) => {
      const active = btn.dataset.type === type;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  };

  const setRatingState = (value) => {
    rateButtons.forEach((btn) => {
      const active = String(btn.dataset.ratingValue) === String(value || "");
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  };

  reactButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const payload = await fetchJSON(reactUrl, {
          method: "POST",
          body: JSON.stringify({
            article_id: articleId,
            type: btn.dataset.type,
          }),
        });

        setReactionState(payload.data.reaction);
        likeCountEl.textContent = payload.data.counts.likes;
        dislikeCountEl.textContent = payload.data.counts.dislikes;
        showToast(payload.data.action === "removed" ? "Реакция убрана" : "Реакция сохранена", "success");
      } catch (_error) {
        // handled in fetchJSON
      }
    });
  });

  if (favoriteBtn) {
    favoriteBtn.addEventListener("click", async () => {
      try {
        const payload = await fetchJSON(favoriteUrl, {
          method: "POST",
          body: JSON.stringify({ article_id: articleId }),
        });

        const active = Boolean(payload.data.favorited);
        favoriteBtn.classList.toggle("is-active", active);
        favoriteBtn.setAttribute("aria-pressed", active ? "true" : "false");
        favoriteCountEl.textContent = payload.data.favorites_count;
        showToast(active ? "Добавлено в избранное" : "Удалено из избранного", "success");
      } catch (_error) {
        // handled in fetchJSON
      }
    });
  }

  if (subscribeBtn) {
    subscribeBtn.addEventListener("click", async () => {
      const categoryId = Number(subscribeBtn.dataset.categoryId || "0");
      if (!categoryId) {
        return;
      }

      try {
        const payload = await fetchJSON(subscribeUrl, {
          method: "POST",
          body: JSON.stringify({ category_id: categoryId }),
        });

        const active = Boolean(payload.data.subscribed);
        subscribeBtn.classList.toggle("is-active", active);
        subscribeBtn.setAttribute("aria-pressed", active ? "true" : "false");
        subscribeBtn.textContent = active ? "Отписаться от категории" : "Подписаться на категорию";
        showToast(active ? "Подписка включена" : "Подписка отключена", "success");
      } catch (_error) {
        // handled in fetchJSON
      }
    });
  }

  rateButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!rateUrl) {
        return;
      }
      try {
        const payload = await fetchJSON(rateUrl, {
          method: "POST",
          body: JSON.stringify({
            article_id: articleId,
            value: Number(btn.dataset.ratingValue),
          }),
        });
        const rating = payload.data?.rating || {};
        setRatingState(payload.data?.user_rating);
        if (ratingAverageEl) {
          ratingAverageEl.textContent =
            typeof rating.average === "number" ? String(rating.average) : "—";
        }
        if (ratingCountEl && typeof rating.count === "number") {
          ratingCountEl.textContent = String(rating.count);
        }
        showToast(payload.data?.action === "removed" ? "Оценка снята" : "Оценка сохранена", "success");
      } catch (_error) {
        // handled in fetchJSON
      }
    });
  });

  if (isAuthenticated) {
    fetchJSON(`${statusUrl}?article_id=${articleId}`, { method: "GET" })
      .then((payload) => {
        const data = payload.data || {};
        if (data.liked) {
          setReactionState("like");
        } else if (data.disliked) {
          setReactionState("dislike");
        } else {
          setReactionState(null);
        }
        if (typeof data.counts?.likes === "number") {
          likeCountEl.textContent = data.counts.likes;
        }
        if (typeof data.counts?.dislikes === "number") {
          dislikeCountEl.textContent = data.counts.dislikes;
        }
        if (favoriteBtn) {
          favoriteBtn.classList.toggle("is-active", Boolean(data.favorited));
          favoriteBtn.setAttribute("aria-pressed", Boolean(data.favorited) ? "true" : "false");
        }
        if (typeof data.user_rating === "number") {
          setRatingState(data.user_rating);
        } else {
          setRatingState(null);
        }
        if (ratingAverageEl && data.rating) {
          ratingAverageEl.textContent =
            typeof data.rating.average === "number" ? String(data.rating.average) : "—";
        }
        if (ratingCountEl && data.rating && typeof data.rating.count === "number") {
          ratingCountEl.textContent = String(data.rating.count);
        }
      })
      .catch(() => {
        // no-op
      });
  }
}

function initCopyLinkButtons() {
  document.querySelectorAll(".js-copy-link-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(window.location.href);
        showToast("Ссылка скопирована", "success");
      } catch (_error) {
        showToast("Не удалось скопировать ссылку", "error");
      }
    });
  });
}

function initShareModal() {
  const modal = document.querySelector("[data-share-modal]");
  const openBtn = document.querySelector(".js-open-share-modal");
  if (!modal || !openBtn) {
    return;
  }

  const close = () => {
    modal.hidden = true;
    document.body.classList.remove("modal-open");
  };

  openBtn.addEventListener("click", () => {
    modal.hidden = false;
    document.body.classList.add("modal-open");
  });

  modal.querySelectorAll(".js-close-share-modal").forEach((btn) => {
    btn.addEventListener("click", close);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      close();
    }
  });
}

function initMatchesFilters() {
  const details = document.querySelector("[data-matches-filters]");
  if (!details) {
    return;
  }

  const hasActive = details.dataset.hasActive === "1";
  if (window.matchMedia("(max-width: 739px)").matches && !hasActive) {
    details.open = false;
  }
}

function initCommentsAjax() {
  const detail = document.querySelector(".news-detail[data-article-id]");
  const form = document.querySelector("[data-comments-form]");
  const list = document.querySelector("[data-comments-list]");
  const count = document.querySelector("[data-comments-count]");

  if (!detail || !list) {
    return;
  }

  const articleId = Number(detail.dataset.articleId);
  const isAuthenticated = detail.dataset.authenticated === "1";
  const addUrl = detail.dataset.commentsAddUrl;
  const deleteUrl = detail.dataset.commentsDeleteUrl;

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const textarea = form.querySelector("textarea[name='text']");
      const text = textarea?.value?.trim() || "";
      if (!text) {
        showToast("Введите текст комментария", "error");
        return;
      }

      try {
        const payload = await fetchJSON(addUrl, {
          method: "POST",
          body: JSON.stringify({ article_id: articleId, text }),
        });

        const empty = list.querySelector("[data-empty-comments]");
        if (empty) {
          empty.remove();
        }

        list.insertAdjacentHTML("afterbegin", payload.data.html);
        textarea.value = "";

        if (count) {
          count.textContent = String(Number(count.textContent || "0") + 1);
        }

        showToast("Комментарий добавлен", "success");
      } catch (_error) {
        // handled in fetchJSON
      }
    });
  }

  list.addEventListener("click", async (event) => {
    const button = event.target.closest(".js-comment-delete");
    if (!button) {
      return;
    }

    const commentId = Number(button.dataset.commentId || "0");
    if (!commentId) {
      return;
    }

    try {
      await fetchJSON(deleteUrl, {
        method: "POST",
        body: JSON.stringify({ comment_id: commentId }),
      });

      const node = list.querySelector(`[data-comment-id="${commentId}"]`);
      if (node) {
        node.remove();
      }

      if (count) {
        const next = Math.max(0, Number(count.textContent || "0") - 1);
        count.textContent = String(next);
        if (next === 0 && !list.querySelector("[data-empty-comments]")) {
          list.innerHTML = '<p class="muted" data-empty-comments>Комментариев пока нет.</p>';
        }
      }

      showToast("Комментарий удален", "success");
    } catch (_error) {
      // handled in fetchJSON
    }
  });
}

function initPasswordToggles() {
  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const inputId = button.dataset.targetId;
      if (!inputId) {
        return;
      }
      const input = document.getElementById(inputId);
      if (!input) {
        return;
      }
      const showing = input.getAttribute("type") === "text";
      input.setAttribute("type", showing ? "password" : "text");
      button.textContent = showing ? "Показать" : "Скрыть";
      button.setAttribute("aria-label", showing ? "Показать пароль" : "Скрыть пароль");
    });
  });
}

function initAuthFieldA11y() {
  document.querySelectorAll(".form-row").forEach((row) => {
    const input = row.querySelector("input, textarea, select");
    const error = row.querySelector(".field-error[id]");
    if (!input || !error) {
      return;
    }
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", error.id);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initMobileMenu();
  initBackToTop();
  initStickyHeader();
  initThemeToggle();
  initSmoothAnchors();
  initAutocomplete();
  initLoadMore();
  initNewsDetailInteractions();
  initCopyLinkButtons();
  initShareModal();
  initMatchesFilters();
  initCommentsAjax();
  initNewsStripScroll();
  initPasswordToggles();
  initAuthFieldA11y();
});

window.showToast = showToast;

