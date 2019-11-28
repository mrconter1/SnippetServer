var getUrlParameter = function getUrlParameter(sParam) {
	var sPageURL = window.location.search.substring(1),
	sURLVariables = sPageURL.split('&'), sParameterName,
			i;

	for (i = 0; i < sURLVariables.length; i++) {
		sParameterName = sURLVariables[i].split('=');

		if (sParameterName[0] === sParam) {
			return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
		}
	}
};

function filterFunction() {
        var input, filter, ul, li, a, i;
        input = document.getElementByName("lang");
        filter = input.value.toUpperCase();
        div = document.getElementById("langList");
        a = div.getElementsByTagName("a");
        for (i = 0; i < a.length; i++) {
                txtValue = a[i].textContent || a[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        a[i].style.display = "";
                } else {
                        a[i].style.display = "none";
                }
        }
}

$(document).ready(function () {
	
	//Initilize page
	loadLatest();
	loadSpecifiedSnippet();
	
	//Loads snippet if specified
	function loadSnippet(snippetName) {
		$.getJSON('/getSnippet/' + snippetName, function(json) {
			funcName = json["funcName"];
			tags = json["tags"];
			input = json["input"];
			output = json["output"];
			deps = json["deps"];
			desc = json["desc"];
			lang = json["lang"];
			code = json["code"];

			$("input[name=funcName]").val(funcName);
			$("input[name=tags]").val(tags);
			$("input[name=input]").val(input);
			$("input[name=output]").val(output);
			$("input[name=deps]").val(deps);
			$("textarea[name=desc]").val(desc);
			$("input[name=lang]").val(lang);
			$("textarea[name=code]").val(code);
		});
	}
	
	function loadSpecifiedSnippet() {
		var parameter = getUrlParameter("id");
		if (parameter != null) {
			loadSnippet(parameter);
		}	
	}
	
	//Load latest snippets and add to snippet list
	function loadLatest() {
		//Fetch latest
		$.getJSON('/latest/', function(json) {
			//Extract list from json
			list = json["results"];
			//Empty list
			$("#snippetList").empty();
			if (list.length > 0) {
				//Populate list with results
				jQuery.each(list, function(index, item) {
					var snippet = '<div id = "snippetName">'+item+'</div>';
					var divider = '<div class="divider"></div>'; 
					$("#snippetList").append(snippet).hide().fadeIn(100);
					if (index != (list.length-1)) {
						$("#snippetList").append(divider).hide().fadeIn(100);
					}
				});
			} else {
				var snippet = '<div id = "snippetName">No snippets..</div>';
				$("#snippetList").append(snippet);
			}
		});
    	}

	//Post a snippet
	$("#addBtn").click(function() {
		$.post("addSnippet/",
			{ 
				funcName: $("input[name=funcName]").val(), 
				tags: $("input[name=tags]").val(), 
				input: $("input[name=input]").val(), 
				output: $("input[name=output]").val(), 
				deps: $("input[name=deps]").val(), 
				desc: $("textarea[name=desc]").val(), 
				lang: $("input[name=lang]").val(), 
				code: $("textarea[name=code]").val()
			},
			function(data) {
				alert(data)
			}
		);
	});
		
	$("#searchBar").keyup(function() {
		if (!this.value) {
			//Reset title
			oldhtml = $('#title').html();
			var newhtml = oldhtml.replace("Search", "Latest");
			$('#title').html(newhtml);
			loadLatest();
	    	} else {
			//Reset title
			oldhtml = $('#title').html();
			var newhtml = oldhtml.replace("Latest", "Search");
			$('#title').html(newhtml);
			//Get search string
			var searchStr = $('#searchBar').val();
			//Fetch json object
			$.getJSON('/search/' + searchStr, function(json) {
				//Extract list from json
				list = json["results"];
				//Empty list
				$("#snippetList").empty();
				if (list.length > 0) {
					//Populate list with results
					jQuery.each(list, function(index, item) {
						var snippet = '<div id = "snippetName">'+item+'</div>';
						var divider = '<div class="divider"></div>'; 
						$("#snippetList").append(snippet).hide().fadeIn(100);
						if (index != (list.length-1)) {
							$("#snippetList").append(divider).hide().fadeIn(100);
						}
					});
				} else {
					var snippet = '<div id = "snippetName">No results..</div>';
					$("#snippetList").append(snippet);
				}
			});
	    	}
	});
	
	$(document).on('mouseenter', '#snippetName', function() {
		var snippetName = $(this).text();
		loadSnippet(snippetName);
	});
	
	$(document).on('mouseup', '#snippetName', function() {
        	var snippetName = $(this).text();
		window.location.href = "?id=" + snippetName;
        });
	
	$(document).delegate('#inputArea', 'keydown', function(e) {
  		var keyCode = e.keyCode || e.which;

		if (keyCode == 9) {
			e.preventDefault();
			var start = this.selectionStart;
			var end = this.selectionEnd;

			// set textarea value to: text before caret + tab + text after caret
			$(this).val($(this).val().substring(0, start)
					+ "\t"
					+ $(this).val().substring(end));

			// put caret at right position again
			this.selectionStart =
			this.selectionEnd = start + 1;
		}
	});

	//----Language input----
	$( "input[name=lang]" ).focus(function() {
		$("#langList").show();
		$('#langList').children('div').each(function () {
			$(this).show();
		});
	});

	$("input[name=lang]").keyup(function() {
		$('#langList').children('div').each(function () {
			var text = $(this).text().toLowerCase();
			var filter = $("input[name=lang]").val();
			if (text.startsWith(filter)) {
				$(this).show();
			} else {
				$(this).hide();
			}
		});
	});	


	$(this).on('click', '#langElement', function() {
		$("input[name=lang]").val($(this).text());		
		$("#langList").hide();
	});

	$("input[name=lang]").keydown(function (e) {    
		if($('#langList').is(':visible')){
			if (e.which == 9) {
				var text = $('#langList').find('div:visible:first').text();
				$("input[name=lang]").val(text);
				e.preventDefault()
				$("#langList").hide();
			}
		} else {
			$("#langList").show();
		}
	});

	$(this).click(function(e) {
		var focus = $("*:focus").attr("name");
		if (focus != "lang") {
			$("#langList").hide();
		}
	});
	
	$(this).keydown(function(e) {
                var focus = $("*:focus").attr("name");
                if (focus != "lang") {
                        $("#langList").hide();
                }
        });

});
