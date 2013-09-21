window.chrso = window.chrso || {};

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

	/*// TODO: AJAX form submission
	$("#click-to-shrink").click(function() {
	});
	*/
});