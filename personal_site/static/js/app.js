$(function() {
  // Prevent form submission using the Enter key
  $(document).on('keypress', 'form', function(e) {
    return e.keyCode != 13;
  });

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
});
