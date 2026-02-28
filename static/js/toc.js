/**
 * Table of Contents — scroll-spy & smooth-scroll
 *
 * How it works:
 *   1. Each heading in .custom-prose has an <a id="…"> anchor.
 *   2. On scroll we find the last anchor whose position is at or above
 *      the current viewport top (plus the sticky-header offset) and
 *      highlight the matching TOC link.
 *   3. Clicking a TOC link smooth-scrolls to the target anchor.
 *
 * Edge-cases handled:
 *   - Anchor positions are recomputed every scroll to survive layout
 *     shifts caused by lazy-loaded images or late-rendered content.
 *   - When the page is scrolled to the very bottom, the last TOC item
 *     is always highlighted — the last section may not have enough
 *     content below it for its anchor to be "scrolled past" normally.
 *   - A 2 px tolerance on the position comparison avoids sub-pixel
 *     rounding mismatches after jQuery's animate().
 */
$(function () {
  const $tocLinks = $("#toc a");

  // Convert the CSS --header-height (rem) to px so we can offset scroll calculations
  const headerHeightRem = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--header-height");
  const remInPx = parseFloat(getComputedStyle(document.documentElement).fontSize);
  const offset = parseFloat(headerHeightRem) * remInPx + 5;

  /**
   * Build a fresh list of {id, top} for every heading anchor.
   * Called on each scroll instead of cached once, because images or
   * other async content can shift element positions after first paint.
   */
  function getAnchors() {
    return $(".custom-prose a[id]")
      .map(function () {
        return { id: this.id, top: $(this).offset().top };
      })
      .get();
  }

  function highlightTocLink(id) {
    $tocLinks.removeClass("active-toc");
    if (id) {
      $tocLinks.filter('[href="#' + id + '"]').addClass("active-toc");
    }
  }

  function onScroll() {
    const anchors = getAnchors();
    if (!anchors.length) return;

    // When the last section is short, the browser physically cannot
    // scroll far enough for its anchor to pass the offset threshold.
    // Detect "at bottom" and force-highlight the last item.
    const atBottom =
      Math.ceil(window.scrollY + window.innerHeight) >=
      document.documentElement.scrollHeight;
    if (atBottom) {
      highlightTocLink(anchors[anchors.length - 1].id);
      return;
    }

    // Walk anchors bottom-up; the first one at or above the scroll
    // line is the section we're currently reading.
    // The 2 px tolerance prevents sub-pixel rounding from causing a
    // mismatch right after a click-driven smooth scroll.
    const scrollTop = $(window).scrollTop() + offset;
    let currentId = null;
    for (let i = anchors.length - 1; i >= 0; i--) {
      if (scrollTop >= anchors[i].top - 2) {
        currentId = anchors[i].id;
        break;
      }
    }
    highlightTocLink(currentId);
  }

  // Smooth-scroll to the target anchor, accounting for the sticky header.
  // The onScroll callback fires after the animation so the highlight
  // updates immediately instead of waiting for the next scroll event.
  $tocLinks.on("click", function (e) {
    e.preventDefault();
    const targetId = $(this).attr("href").substring(1);
    const $target = $("#" + targetId);
    if ($target.length) {
      const scrollTo = $target.offset().top - offset;
      $("html, body").animate({ scrollTop: scrollTo }, 300, onScroll);
    }
  });

  // Throttle scroll events via requestAnimationFrame for performance
  let ticking = false;
  $(window).on("scroll", function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        onScroll();
        ticking = false;
      });
      ticking = true;
    }
  });

  onScroll(); // highlight the active section on initial page load
});
