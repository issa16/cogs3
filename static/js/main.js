$(document).ready(function () {
	
	// Initialise date picker
        $('.datepicker').datepicker({
            dateFormat: 'yy-mm-dd'
        });

        // Handle user membership request update
        $(".membership-status").change(function () {
            var request_id = $(this).nextAll("input[name='request']").first().val();
            var project_id = $(this).nextAll("input[name='project']").first().val();
            var status_id = $(this).val();
            var csrf_token = $("#csrf_token").val();
            var data = {
                "request_id": request_id,
                "project_id": project_id,
                "status": status_id,
                "csrfmiddlewaretoken": csrf_token
            };
            $.ajax({
                type: "POST",
                url: $(location).attr('href') + "update/" + request_id + "/",
                data: data,
                dataType: "json",
                success: function () {
                    location.reload();
                },
                error: function (a) {
                    location.reload();
                }
            });
        });

        $("#password-reset").submit(function (event) {
            event.preventDefault();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
            // Ensure password fields match
            var password = $('input[name=password]').val();
            var password_confirm = $('input[name=password-confirm]').val();
            if (password != password_confirm) {
                $('#form-errors').text('{% trans "The passwords you have entered do not match." %}');
                $('#form-errors').removeClass('d-none');
            } else {
                $('#form-errors').addClass('d-none');
                // Submit a password reset request
                $.ajax({
                    type: 'POST',
                    //url: "{% url 'scw-password-reset' %}", // Fix
                    url: window.location.origin + '/accounts/scw/password-reset/',
		    data: {
                        'password': password,
                        'password_confirm': password_confirm,
                        'csrfmiddlewaretoken': csrfmiddlewaretoken,
                    },
                    dataType: 'json',
                    encode: true,
                    success: function (msg) {
                        // Hide password reset form
                        $('#password-policy').addClass('d-none');
                        $('#password-reset > .modal-footer > .btn-primary').addClass('d-none');
                        // Show success message
                        $('#form-success').text(msg.data);
                        $('#form-success').removeClass('d-none');
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        // Hide any success messages
                        $('#form-success').addClass('d-none');
                        // Show error message
                        $('#form-errors').text('Invalid password reset request.');
                        $('#form-errors').removeClass('d-none');
                    },
                });
            }
        });
});
