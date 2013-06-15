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

function refresh_captcha() {
	Recaptcha.create(window.chrso.recaptcha,
		"recaptcha-goes-here",
		{
			theme: "clean",
			callback: function() {}
		}
	);
}

window.chrso = window.chrso || {recaptcha: null};
window.chrso.last_id = 0;
window.chrso.last_err = 0;


$(function() {
	$("#customize-extras").hide();

	$(".enable-me").each(function() {
		$(this).removeAttr("disabled");
	});

	$('.tooltips').tipsy({
		gravity: "n",
		html: true
	});

	$('#customize').click(function () {
		$('#customize-extras').slideToggle();
	});

	if ('recaptcha' in window.chrso) {
		refresh_captcha();
	}

	/* old code: */
	$("form#shrink-url").submit(function() {
		console.log("Is: " + $(this).attr('method'));
		console.log($(this).serialize());
		$.post(
			$(this).attr('action'),
			$(this).serialize(),
			function(data, textStatus, jqXHR) {
				if (data.error == "true") {
					flash(data.message, "error");
					return;
				}
				var s1 = window.chrso.last_id++, s2 = window.chrso.last_id++, s3 = window.chrso.last_id++;
				var $url = $('<div class="chr-result"></div>');

				var $close_ = $('<span class="close-btn right">&#10006;</span>');

				$close_.click(function() {
					$(this).parent().slideUp(function() {
						$(this).remove();
					});
				});

				var $long_ = $('<div></div>')
						.append('<h3>Long url</h3>')
						.append('<input type="text" name="shorten-'+s1+'" class="chr-text-long shorten-'+s1+'" value="'+data.given+'" disabled="disabled" />');
				var $short_ = $('<div></div>')
						.append('<h3>Short url</h3>')
						.append('<input type="text" name="shorten-'+s2+'" class="chr-text-long shorten-'+s2+'" value="'+data.url+'" readonly="readonly" />');
				var $delete_ = $('<div></div>')
						.append('<h3>Delete url (SAVE THIS)</h3>')
						.append('<input type="text" name="shorten-'+s3+'" class="chr-text-long shorten-'+s3+'" value="'+data.delete+'" readonly="readonly" />');
				$url.append($close_, $long_, $short_);
				if (data.delete != "") {
					$url.append($delete_);
				}
				$url.appendTo($('#chr-results-group'));
				shrink('.shorten-' + s1);
				shrink('.shorten-' + s2);
				if (data.delete != "") {
					shrink('.shorten-' + s3);
				}
				$("input#chr-text-long").val("http://");
				$("input#chr-text-short").val("");
				$("input#chr-check-delete").attr('checked', false);
				flash(data.message);
			}
		);
		return false;
	});

	$("div#form-modal").dialog({
		autoOpen: false,
		closeOnEscape: true,
		draggable: false,
		hide: "clip",
		resizable: false,
		height: 300,
		width: 475,
		modal: true,
		buttons: {
			"Submit": function() {
				// We handle failures in the submit handler.
				$("form#shrink-url").submit();
				refresh_captcha();
				$(this).dialog("close");
			},
			"Cancel": function() {
				$(this).dialog("close");
			}
		},
		close: function() {
			// don't really need to do anything.
		}
	});

	$("button#click-to-shrink").click(function() {
		$("div#form-modal").dialog("open");
	});

	// This is to compensate for the fact that we're
	//  serializing the form to send it.
	// If we don't do this, the modal will be outside
	//  of the form, and hence won't submit, ending
	//  in some nasty 400 Bad Request replies, etc.
	$('div[role="dialog"]').appendTo("form#shrink-url");
	/* end old code */
});