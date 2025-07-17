$(function () {
  if (localStorage.getItem("sidebar") === "open") {
    $(
      "#nav-sidebar, #main-content, #toggle-sidebar-desktop, #toggle-sidebar-mobile"
    ).addClass("open");
  }
});

const darkModeKey = "darkmode";

function toggleDarkMode() {
  $("html").toggleClass("dark");
  if ($("html").hasClass("dark")) {
    localStorage.setItem(darkModeKey, "enabled");
  } else {
    localStorage.setItem(darkModeKey, "disabled");
  }
}

const navKey = "sidebar";

function toggleNav() {
  this.classList.toggle("open");
  $("#nav-sidebar, #main-content").toggleClass("open");
  // Update localStorage based on sidebar state
  if ($("#nav-sidebar").hasClass("open")) {
    localStorage.setItem(navKey, "open");
  } else {
    localStorage.setItem(navKey, "closed");
  }
}
