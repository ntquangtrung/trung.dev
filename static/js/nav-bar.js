$(function () {
  $("#toggle-sidebar-desktop, #toggle-sidebar-mobile").on("click", function () {
    $("#nav-sidebar, #toggle-sidebar-desktop, #main-content").toggleClass(
      "open"
    );
  });

  $("#toggle-darkmode").on("click", function () {
    $("html").toggleClass("dark");
    if ($("html").hasClass("dark")) {
      localStorage.setItem("darkmode", "enabled");
    } else {
      localStorage.setItem("darkmode", "disabled");
    }
  });
});
