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
        input = document.getElementByName("lang"); filter = input.value.toUpperCase();
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

function sanitize(str) {
	str = str.replace(/</g, "﹤").replace(/>/g, "﹥");
	return str
}

$(document).ready(function () {

	var buttonState = "add";
	
	//Initilize page
	var url = window.location.href;
	var match = url.match(new RegExp(".com/" + "(.+)" + "/"));
	var page = "";
	if (match != null) {
		page = match[1];
	}

	if (page === "list") {
		loadListPage();
	} else {
		loadLatest();
	}
	
	//If certain snippet is to be loaded
	loadSpecifiedSnippet();

	//Set initial language
	if ($.cookie("lang")) {
		var lang = $.cookie("lang");
		$(".langOpt").html(lang);
	}


	function isAuthenticated() {
		$.getJSON('/isAuth/', function(json) {
			auth = json['authenticated'].toString().trim();
			if (auth === "true") {
				loadAdminTools();
			} 
		});
	}

	function loadAdminTools() {
		$('.deleteBtn').each(function () {
			$(this).show();
		});
	}

	//Handles list page
	function loadListPage() {
		$.getJSON('/getSnippetCount/', function(json) {

			var resultsPerPage = 15;

			var page = url.match(new RegExp("list/" + "(.+)"))[1];
			var offset = (page-1)*resultsPerPage;
			loadRange(offset, resultsPerPage);
			
			var count = Number(sanitize(json["count"]));
			var currentPage;
			var numOfPages = Math.ceil(count/resultsPerPage);

			var content = '<p id = "previousPage">&#60;<p>';
			$(content).hide().appendTo("#pageChooser").fadeIn(1000);
			for (currentPage = 1; currentPage <= numOfPages; currentPage++) {
				var content = '<p class="page">' + currentPage + '</p>';
				$(content).hide().appendTo("#pageChooser").fadeIn(1000);
			}
			var content = '<p id = "nextPage">&#62;<p>';
			$(content).hide().appendTo("#pageChooser").fadeIn(1000);

			if (page === "1") {
				$("#previousPage").hide();
			}
			var pageCount = $('.page').size();
			$(".page").each( function( index, element ){
				var number = $(this).text();
				if (number === page) {
					$(this).css("font-weight","Bold");
					if (Number(number) === pageCount) {
						$("#nextPage").hide();
					}
				}
			});
			$(".page").click(function() {
				var page = $(this).text();
				window.location.href = '/list/' + page;
			});
			$("#previousPage").click(function() {
				var prevPage = Number(page) - 1;
				window.location.href = '/list/' + prevPage;
			});
			$("#nextPage").click(function() {
				var nextPage = Number(page) + 1;
				window.location.href = '/list/' + nextPage;
			});
			$(".backBtn").click(function() {
				window.location.href = '/repo/';
			});
		});
	}

	//Loads snippet if specified
	function loadSnippet(snippetID) {
		$.getJSON('/getSnippet/' + snippetID, function(json) {
			funcName = sanitize(json["funcName"]);
			tags = sanitize(json["tags"]);
			input = sanitize(json["input"]);
			example = sanitize(json["example"]);
			deps = sanitize(json["deps"]);
			desc = sanitize(json["desc"]);
			lang = sanitize(json["lang"]);
			code = sanitize(json["code"])

			$("input[name=funcName]").val(funcName);
			$("input[name=tags]").val(tags);
			$("input[name=input]").val(input);
			$("input[name=example]").val(example);
			$("input[name=deps]").val(deps);
			$("textarea[name=desc]").val(desc);
			$("input[name=lang]").val(lang);
			$("textarea[name=code]").val(code);

			$("#pinned").html(funcName);
		});
	}

	function loadSpecifiedSnippet() {
		var parameter = getUrlParameter("id");
		if (parameter != null) {
			loadSnippet(parameter);
		}	
	}
	
	function populateRangeList(json) {
		//Extract list from json
		list = json["results"];
		//Empty list
		$("#snippetRangeList").empty();
		if (list.length > 0) {
			//Populate list with results
			jQuery.each(list, function(index, item) {
				var snippet = '<div class = "snippetName">';
				snippet += '<div class="nameDiv">' + sanitize(item.funcName) + "</div>";
				snippet += '<div class="deleteBtn" style="display:none"><b class="deleteBtnTxt">Delete</b></div>';
				snippet += '<input type="hidden" value="' + sanitize(item.id.toString()) + '" />';
				snippet += '</div>';
				var divider = '<div class="divider"></div>';
				$(snippet).hide().appendTo("#snippetRangeList").fadeIn(250);
				if (index != (list.length-1)) {
					$("#snippetRangeList").append(divider).hide().fadeIn(250);
				}
			});
    			$("#pageChooser").hide();
			$(".divider").each(function(i) {
    				$(this).hide();
			});
			$(".snippetName").each(function(i) {
    				$(this).hide();
			});
			$(".snippetName").each(function(i) {
				$(this).delay(15 * i).fadeIn(100);
			});
			$(".divider").fadeIn(1000);
			$("#pageChooser").fadeIn(1000);
		} else {
			var snippet = '<div class = "snippetName">No snippets..</div>';
			$("#snippetRangeList").append(snippet);
		}
	}

	function populateList(json) {
		//Extract list from json
		list = json["results"];
		//Empty list
		$("#snippetList").empty();
		if (list.length > 0) {
			//Populate list with results
			jQuery.each(list, function(index, item) {
				var snippet = '<div class = "snippetName">';
				snippet += '<div class="nameDiv">' + sanitize(item.funcName) + "</div>";
				snippet += '<div class="deleteBtn" style="display:none"><b class="deleteBtnTxt">Delete</b></div>';
				snippet += '<input type="hidden" value="' + sanitize(item.id.toString()) + '" />';
				snippet += '</div>';
				var divider = '<div class="divider"></div>';
				$("#snippetList").append(snippet).hide().fadeIn(100);
				if (index != (list.length-1)) {
					$("#snippetList").append(divider).hide().fadeIn(100);
				}
			});
			$(".divider").each(function(i) {
    				$(this).hide();
			});
			$(".snippetName").each(function(i) {
    				$(this).hide();
			});
			$(".snippetName").each(function(i) {
				$(this).delay(50 * i).fadeIn(250);
			});
			$(".divider").fadeIn(500);
			isAuthenticated();
		} else {
			var snippet = '<div class = "snippetName">No snippets..</div>';
			$("#snippetList").append(snippet);
		}
	}
	
	//Load latest snippets and add to snippet list
	function loadLatest() {
		//Fetch latest
		$.getJSON('/latest/', function(json) {
			populateList(json);
		});
    	}
	//
	//Load range of snippets and add to snippet list
	function loadRange(a, b) {
		//Fetch latest
		$.getJSON('/getSnippetsBetween/' + a + '/' + b, function(json) {
			populateRangeList(json);
		});
    	}

	//Post a snippet
	$("#addBtn").click(function() {
		if (buttonState == "clear") {
			buttonState = "add";
			$(".btnTxt").html("Add Snippet");	

			$("input[name=funcName]").val("");
			$("input[name=tags]").val("");
			$("input[name=input]").val("");
			$("input[name=example]").val("");
			$("input[name=deps]").val("");
			$("textarea[name=desc]").val("");
			$("input[name=lang]").val("");
			$("textarea[name=code]").val("");

			return 0;
		}
		$.post("addSnippet/",
			{ 
				funcName: $("input[name=funcName]").val(), 
				tags: $("input[name=tags]").val(), 
				input: $("input[name=input]").val(), 
				example: $("input[name=example]").val(), 
				deps: $("input[name=deps]").val(), 
				desc: $("textarea[name=desc]").val(), 
				lang: $("input[name=lang]").val(), 
				code: $("textarea[name=code]").val()
			},
			function(data) {
				alert(data)
				document.location.href="/";
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
			var lang = $('.langOpt').first().text().trim();
			//Fetch json object
			$.getJSON('/search/' + lang + '/' + searchStr, function(json) {
				populateList(json);
			});
	    	}
	});
	
	$(document).on('mouseenter', '.snippetName', function() {
		if ($("#pinned").length) {
			return;
		}
		var snippetID = $(this).find('input').val();
		loadSnippet(snippetID);
		buttonState = "clear";
		$(".btnTxt").html("Clear fields");	
	});
	
	$(document).on('mouseup', '.snippetName', function(e) {
		if ($(event.target).is('.snippetName') || $(event.target).is('.nameDiv')){
			var snippetID = $(this).find('input').val();
			window.location.href = "/repo/?id=" + snippetID;
		}
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

	//Language filtering
	$(document).on('mouseenter', '#language', function() {
		var currentLang = $('#language').text().trim();
		var langList = [	"javascript", 
					"python2", 
					"python3", 
					"java", 
					"php", 
					"cpp", 
					"csharp", 
					"typescript", 
					"shell", 
					"c", 
					"ruby"];
		$.each(langList , function(index, val) { 
			if(currentLang == val) {
				return true;
			}
			var lang = '<div class = "langOpt">'+val+'</div>';
			$("#language").append(lang).fadeIn(100);
			$('.langOpt').css('border-radius', '0px');
		});
		$('.langOpt').first().css('border-radius', '5px 0px 0px 0px');
	});

	$(document).on('mouseleave', '#language', function() {
		$('.langOpt').not(':first').remove();
		$('.langOpt').css('border-radius', '5px');
	});

	$(this).on('click', '.snippetListLink', function() {
		document.location.href="/list/1";
	});

	$(this).on('click', '.langOpt', function() {
		var lang = $(this).text();
		$('.langOpt').not(':first').remove();
		$('.langOpt').text(lang);
		$('.langOpt').css('border-radius', '5px');
		$.cookie("lang", lang);
	});

	//---Login---
	$(this).on('click', '.loginBtn', function() {
		if ($(".loginPanel").is(":visible")) {
			$(".loginPanel").fadeOut(200);
		} else {
			$(".loginPanel").fadeIn(200);
			$("input[name='loginUser']").focus();
		}
        });
	
	$('.loginInput').keypress(function (e) {
 		var key = e.which;
 		if(key == 13)
  		{
			$.post("login/",
			{
				username: $("input[name=loginUser]").val(),
				password: $("input[name=loginPass]").val()
			},
			function(data) {
				location.reload(true);
			}
		);

  		}
	});   	
	
	//---Snippet pinning---
	//Set pinned snippet if selected
	if (window.location.href.indexOf("?id") > -1) {
		var id = getUrlParameter("id");
		$(".infoDiv").append('<p id = "title">Pinned Snippet</p>');
		var snippet = '<div class = "snippetName">';
		snippet += '<div id = "pinned" class="nameDiv">' + sanitize(name) + "</div>";
		snippet += '<b class="unpinBtnTxt">Unpin</b>';
		snippet += '<input type="hidden" value="' + sanitize(id) + '" />';
		snippet += '</div>';
		var divider = '<div class="divider"></div>';
		$(".infoDiv").append(snippet).hide().fadeIn(100);
		loadSpecifiedSnippet();
		$('#pinned').css('background-color', '#cccccc');
		$('#pinned').css('width', '100%');
		$('#pinned').css('padding', '5px');
		$('#pinned').css('border-radius', '7px 0px 0px 7px');
	}

	//Disables hovering effect for pinned snipped
	$(".snippetName").hover(function() {
  		$(this).css("background-color","transparent")
	});
	
	$(".unpinBtnTxt").click(function() {
		document.location.href="/repo/";
	});

	//---Admin---
	$(this).on('click', '.deleteBtnTxt', function(e) {
		var res = confirm('Are you sure?');
		if (res && $(event.target).is('.deleteBtnTxt')){
			var idValue = $(this).parent().parent().find('input').val();
			$.post("delete/",
			{
				id: idValue,
			},
			function(data) {
				document.location.href="/";
			});
		}
        });
	
});


