// Light/dark theme toggle shared by the static reader pages and the explorer.
// The <head> runs a one-line snippet that applies a stored choice before
// paint; this script wires [data-theme-toggle] buttons and announces changes
// with an "np-themechange" event so the map can swap basemap tiles.
(function () {
  "use strict";
  var KEY = "np-theme";
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function stored() {
    try { return localStorage.getItem(KEY); } catch (_error) { return null; }
  }

  function current() {
    var explicit = document.documentElement.getAttribute("data-theme");
    if (explicit === "light" || explicit === "dark") return explicit;
    return media && media.matches ? "dark" : "light";
  }

  function label(theme) {
    return theme === "dark" ? "Switch to light theme" : "Switch to dark theme";
  }

  function sync() {
    var theme = current();
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute("aria-label", label(theme));
      buttons[i].setAttribute("title", label(theme));
    }
    document.dispatchEvent(new CustomEvent("np-themechange", { detail: { theme: theme } }));
  }

  function set(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch (_error) { /* private mode */ }
    sync();
  }

  function toggle() {
    set(current() === "dark" ? "light" : "dark");
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest && event.target.closest("[data-theme-toggle]");
    if (button) toggle();
  });
  if (media && media.addEventListener) {
    media.addEventListener("change", function () { if (!stored()) sync(); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", sync);
  else sync();

  window.NepalTheme = { current: current, set: set, toggle: toggle };
})();
