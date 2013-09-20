function shrink(i, ext) {
	/* Shrink an input's width down
	   to the size of its text.
	*/
	ext = ext || 10;
	var $input = $(i),
		$tmp = $('<span class="resize-test" />');
	$tmp.text($input.val());
	$('body').append($tmp);
	var width = $tmp.width();
	$tmp.remove();
	var widthToSet = (ext + width) + 'px';
	$input.width(widthToSet);
	console.log("input: " + i + ", ext: " + ext + ", width: " + width + "px, toSet: " + widthToSet);
}

function flash(msg, category) {
	var num = window.chrso.last_err++;
	category = category || "success";
	$err = $('<p class="flash flash-' + category + ' flash-num-' + num + '">' + msg + '</p>');
	$('#flashes').append($err);
	setTimeout(function() {
		$err.slideUp("slow", function() {
			$err.remove();
		});
	}, 1000 * 2);
}

window.chrso = window.chrso || {recaptcha: null};
window.chrso.last_id = 0;
window.chrso.last_err = 0;


$(function() {
	$("#customize-extras").hide();

	$(".enable-me").each(function() {
		$(this).removeAttr("disabled");
	});

	$(".tooltips").tipsy({
		gravity: "n",
		html: true
	});

	$("#customize").click(function () {
		$("#customize-extras").slideToggle();
		return false; // so we don't submit the form..
	});

	$("#click-to-shrink").click(function() {
		// TODO: new form submission (via jQuery) goes here
	});
});