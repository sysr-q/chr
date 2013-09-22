var time = 1000 * 2; // Two seconds.
var next_timer = time;
$(document).ready(function() {
	$('#flashes p').each(function(index) {
		setTimeout(function() {
			var p = '.flash-num-' + (index + 1);
			$(p).slideUp("slow", function() {
				$(p).remove();
			})
		}, next_timer);
		next_timer += time;
	});
});