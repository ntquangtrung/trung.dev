const darkModeKey = "darkmode";

if (localStorage.getItem(darkModeKey) === "enabled") {
  $("html").addClass("dark");
}

function toggleDarkMode() {
  $("html").toggleClass("dark");
  if ($("html").hasClass("dark")) {
    localStorage.setItem(darkModeKey, "enabled");
  } else {
    localStorage.setItem(darkModeKey, "disabled");
  }
}

function toggleNav() {
  this.classList.toggle("open");
  $("#nav-sidebar, #main-content").toggleClass("open");
}

// Close sidebar on mobile when a nav link is clicked
$("#nav-sidebar a").on("click", function () {
  if (!window.matchMedia("(min-width: 768px)").matches) {
    $("#nav-sidebar, #main-content, #toggle-sidebar-mobile").removeClass(
      "open",
    );
  }
});
