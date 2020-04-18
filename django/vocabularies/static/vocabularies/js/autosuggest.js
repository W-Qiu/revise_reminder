/* 
listen to search_input
construct ES query and send
use response to populate autosuggest div
 */

var BaseURL = 'http://localhost:9200/';
var index = 'vocab/';

var throttledInput = _.throttle(function () {
    $("ul.autosuggest").empty();
    var query = {
        suggest: {
            wordSuggest: {
                prefix: $('#search_input').val(),
                completion: {
                    field: 'word'
                    // fuzzy: true
                },
            },
        },
    };

    $.ajax({
        url: BaseURL + index + '_search',
        type: 'post',
        dataType: 'json',
        success: function (data) {
            var words = data.suggest.wordSuggest[0].options;
            for (let i = 0; i < words.length; i++) {
                let word = words[i].text;
                $("ul.autosuggest").append(
                    "<li class='autosuggest'>" + word + "</li>")
            }
        },
        contentType: 'application/json',
        data: JSON.stringify(query),
    });
}, 500);

$(document).ready(function () {
    $("#search_input").keyup(throttledInput);

    // input focus out, clean results
    $("#search_input").focusout(function () {
        $("ul.autosuggest").empty();
    })

    // mouseover change background color
    // $("li.autosuggest").mouseover(function () {
    //     $(this).addClass('mouseover');
    // });

    // $("li.autosuggest").mouseleave(function () {
    //     $(this).removeClass('mouseover');
    // });
});