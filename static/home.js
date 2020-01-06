$(document).ready(function () {

	if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {

		$(".container").css("padding-top", "300px");
		$(".container").css("padding-bottom", "300px");
		$(".container").css("justify-contetn", "");
		$(".container").css("height", "100vh");
		
		$("#logoSpan").css("font-size", "80px");
		$("#betaSpan").css("font-size", "30px");
		$("#titleSpan").css("font-size", "45px");

		$("#info").css("margin-top", "50px");
		$("#infoSpan").css("font-size", "45px");
		
		$("#demo").css("margin-top", "50px");
		
		$("#portal").css("flex-direction", "column");
		$("#portal").css("margin-top", "50px");

		$(".button").css("margin-top", "25px");
		$(".button").css("margin-bottom", "25px");
		$(".button").css("font-size", "70px");
		$(".button").css("width", "90%");
		$(".button").css("border-radius", "15px");

	}

	$("#plugin").click(function() {
        	window.location.href = 'https://github.com/mrconter1/SnippetDepot/';
	});
	$("#wiki").click(function() {
        	window.location.href = 'https://github.com/mrconter1/SnippetDepot/';
	});
	$("#reddit").click(function() {
        	window.location.href = 'https://www.reddit.com/r/snippetdepot';
	});
	$("#repo").click(function() {
        	window.location.href = '/repo/';
	});
});

