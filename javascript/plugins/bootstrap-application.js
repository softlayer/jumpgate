! function ($) {
  $(function () {
    if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
      var msViewportStyle = document.createElement("style");
      msViewportStyle.appendChild(document.createTextNode("@-ms-viewport{width:auto!important}"));
      document.getElementsByTagName("head")[0].appendChild(msViewportStyle)
    }
    var $window = $(window);
    var $body = $(document.body);
    var navHeight = $(".navbar").outerHeight(true) + 10;
    $body.scrollspy({
      target: ".sidebar",
      offset: navHeight
    });
    $window.on("load", function () {
      $body.scrollspy("refresh")
    });
    $(".docs-container [href=#]").click(function (e) {
      e.preventDefault()
    });
    setTimeout(function () {
      var $sideBar = $(".sidebar");
      $sideBar.affix({
        offset: {
          top: function () {
            var offsetTop = $sideBar.offset().top;
            var sideBarMargin = parseInt($sideBar.children(0).css("margin-top"), 10);
            var navOuterHeight = $(".docs-nav").height();
            return (this.top = offsetTop - navOuterHeight - sideBarMargin)
          },
          bottom: function () {
            return (this.bottom = $(".footer").outerHeight(true))
          }
        }
      })
    }, 100);
    setTimeout(function () {
      $(".top").affix()
    }, 100);
    $(".tooltip-demo").tooltip({
      selector: "[data-toggle=tooltip]",
      container: "body"
    });
    $(".tooltip-test").tooltip();
    $(".popover-test").popover();
    $(".docs-navbar").tooltip({
      selector: "a[data-toggle=tooltip]",
      container: ".docs-navbar .nav"
    });
    $("[data-toggle=popover]").popover();
    $("#fat-btn").click(function () {
      var btn = $(this);
      btn.button("loading");
      setTimeout(function () {
        btn.button("reset")
      }, 3000)
    })
  })
}(window.jQuery);