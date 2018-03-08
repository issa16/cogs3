$(document).ready(function() {
	// Initialise date pickers
	$("#id_start_date").datepicker();
	$("#id_end_date").datepicker();

	// Handle user membership request update
	$(".membership-status").change(function() {
		var request = $(this).nextAll("input[name='request']").first().val();
		var project = $(this).nextAll("input[name='project']").first().val();
		var status = $(this).val();
		var csrf_token = $('#csrf_token').val();
		var data = {
			'request_id': request,
			'project_id': project,
			'status': status,
			'csrfmiddlewaretoken': csrf_token
		};
		$.ajax({
			type: "POST",
			url: "/projects/memberships/user-requests/update/" + request + "/",
			data: data,
			dataType: 'json',
			success: function() {
				location.reload();
			},
			error: function(a) {
				location.reload();
			}
		});
	});
});
