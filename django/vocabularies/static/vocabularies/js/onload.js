/*
 * ajax to fetch image from cloud API
 */
// ajax variables
var word_id = document.querySelector('input[name=word_id]').value
var URL = '/word_images/?word_id=' + word_id;
var xhr = new XMLHttpRequest();
var timer_id;
xhr.open('GET', URL);

window.onload = function(){
	// ajax request, STOPPED NOW, activate when cloud is setup
	// xhr.send();

	// highligh word
	var num_picks = $("#num_picks").text();
	for (var i = 0; i < num_picks; i++) {
		var pick = $(`#pick${i}`).text();
		var replacement = '<span style="background-color: yellow">' + pick + '</span>';
		var sentence = $(`#example${i}`).text();
		var new_sentence = sentence.replace(pick, replacement);
		$(`#example${i}`).html(new_sentence);
	};

}

xhr.onload = function() {
	url = xhr.response;
	document.getElementById("word_image").src = url;
};