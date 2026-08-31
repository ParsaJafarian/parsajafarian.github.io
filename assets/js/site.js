"use strict";

/* Theme toggle. The initial value is applied by an inline script in <head>
   so the page never flashes the wrong palette. */

(function () {
	var btn = document.querySelector(".theme-toggle");
	if (!btn) return;

	function label() {
		var dark = document.documentElement.getAttribute("data-theme") === "dark";
		btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
	}

	btn.addEventListener("click", function () {
		var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
		document.documentElement.setAttribute("data-theme", next);
		try {
			localStorage.setItem("theme", next);
		} catch (e) {
			/* storage unavailable — the choice just won't persist */
		}
		label();
	});

	label();
})();
