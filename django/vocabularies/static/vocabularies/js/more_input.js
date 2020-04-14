$(document).ready(function(){
	$(".more_example").click(function(){
		$(".example_wrapper").append('<input type="text" class="form-control" name="example" value="">');
	});

	$(".more_interpretation").click(function(){
		$(".interpretation_wrapper").append('<input type="text" class="form-control" name="interpretation" value="">');
	});
});

