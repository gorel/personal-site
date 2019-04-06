$(function() {
  // Anchor tag override
  $('a[data-method]').click(function(e) {
    method = $(this).data('method');
    action = $(this).attr('href');
    csrf   = $('meta[name=csrf-token]').attr('content');

    // Allow GET requests to go through normally
    if(method == 'GET') return true;
    // Prevent default request actions from executing
    e.preventDefault();

    // Create a form object with the appropriate method and action
    var form = $('<form></form>');
    form.attr('method', method);
    form.attr('action', action);
    form.append('<input type="hidden" name="csrf_token" value="'+csrf+'" />');

    // Require confirm if specified
    confirm_message = $(this).data('confirm');
    if(confirm_message && !window.confirm(confirm_message)) return true;

    // Submit the form
    $(document.body).append(form);
    form.submit();
  });

  // Add hljs to all pre blocks for better formatting
  $("pre").addClass("hljs");
});

// listen for click events originating from elements with href starting with #
$("body").on("click.scroll-adjust", '[href^="#"]', function (e) {
  var $nav

  // make sure navigation hasn"t already been prevented
  if ( e && e.isDefaultPrevented() ) return

  // get a reference to the offending navbar
  $nav = $("div.navbar")

  // check if the navbar is fixed
  if ( $nav.css("position") !== "fixed" ) return

  // listen for when the browser performs the scroll
  $(window).one("scroll", function () {
    // scroll the window up by the height of the navbar
    window.scrollBy(0, -2 * $nav.height())
  });

});

function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function deleteCookie(name) {
    createCookie(name, "", -1);
}
