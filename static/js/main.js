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
                url: "{% url 'project-user-membership-request-update' %}" + request_id + "/",
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
});
