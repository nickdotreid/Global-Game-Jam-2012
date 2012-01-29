$(document).ready(function(event){
	$(".button").bind("mouseenter",function(){
		$(this).addClass("hover");
	}).bind("mouseleave",function(){
		$(this).removeClass("hover");
	});
})