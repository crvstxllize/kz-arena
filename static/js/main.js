document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      const isOpen = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  const backToTopBtn = document.getElementById("back-to-top");
  if (backToTopBtn) {
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

  const kindFilterButtons = document.querySelectorAll("[data-kind-filter]");
  const filterTargets = document.querySelectorAll("#news-grid [data-kind], .top-list [data-kind]");

  if (kindFilterButtons.length > 0 && filterTargets.length > 0) {
    kindFilterButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const selectedKind = button.dataset.kindFilter;

        kindFilterButtons.forEach((item) => {
          const isActive = item === button;
          item.classList.toggle("is-active", isActive);
          item.setAttribute("aria-pressed", String(isActive));
        });

        filterTargets.forEach((target) => {
          const targetKind = target.dataset.kind;
          const shouldShow = selectedKind === "all" || selectedKind === targetKind;
          target.classList.toggle("is-hidden-by-filter", !shouldShow);
        });
      });
    });
  }
});

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

window.showToast = showToast;
