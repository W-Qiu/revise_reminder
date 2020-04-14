Mousetrap.bind('enter', show_all);
Mousetrap.bind('space', show_example);
Mousetrap.bind('t', activate_TTT_modal);

function show_all(){
  show_example();
  show_interpretation();
  
  Mousetrap.unbind('enter', show_all);
  Mousetrap.bind('enter', yes);
}

function yes(){
  document.getElementById("yes_btn").click();
}

function show_example(){
  var example = document.getElementsByClassName("example");
  var i;
  for (i = 0; i < example.length; i++) {
    if (example[i].style.visibility == "hidden") {
      example[i].style.visibility = "visible";
    }
  }

  var show_example_btn = document.getElementById("show_example_btn");
  var show_interp_btn = document.getElementById("show_interp_btn");
  show_example_btn.style.display = "none";
  show_interp_btn.style.display = "block";

  if (document.getElementById("log") != null){
    document.getElementById("log").style.visibility = "visible";
    document.getElementById("TTT_modal_btn").style.display = "none";
  }

  Mousetrap.unbind('space', show_example);
  Mousetrap.unbind('t', activate_TTT_modal);
  Mousetrap.bind('space', show_interpretation);

  document.getElementById("word_image").style.display = "block";

  // for type_to_test
  // var reading_rate = 0.8; // seconds per word, 25 words per 15s = 0.6
  // var total_length = 0;
  //   $(".example").each(function(){
  //       totqal_length += $(this).text().split(' ').length
  //   });
  //   if (total_length != 0) {
  //     timer_id = setTimeout(
  //             function() {
  //                 activate_TTT_modal()
  //             }, total_length*reading_rate*1000);
  //   } else {
    
  //   }
}


function show_interpretation(){
  window.clearTimeout(timer_id);
  var interp = document.getElementsByClassName("interpretation");
  for (i = 0; i < interp.length; i++) {
    if (interp[i].style.visibility == "hidden") {
      interp[i].style.visibility = "visible";
    }
  }

  var yes_btn = document.getElementById("yes_btn");
  var next_word_btn = document.getElementById("next_word_btn");
  var show_interp_btn = document.getElementById("show_interp_btn");
  yes_btn.style.display = "none";
  next_word_btn.style.display = "block";
  show_interp_btn.style.display = "none";

  Mousetrap.unbind('enter', show_all);
  Mousetrap.bind('enter', yes);
  Mousetrap.unbind('space', show_interpretation);
  Mousetrap.bind('space', no);
}

function no(){
  document.getElementById("next_word_btn").click();
}

function activate_TTT_modal(){
  window.clearTimeout(timer_id);
  document.getElementById("TTT_modal_btn").click();
  document.getElementById("TTT_input").focus();
}