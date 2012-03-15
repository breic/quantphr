function setCookie(cookieName, cookieValue, nDays) {
	var today = new Date();
	var expire = new Date();
	if (nDays == null || nDays == 0) nDays = 1;
	expire.setTime(today.getTime() + 3600000*24*nDays);
	document.cookie = cookieName + "=" + escape(cookieValue) + ";expires="+expire.toGMTString();
}

function readCookie(cookieName) {
	var theCookie=" "+document.cookie;
	var ind=theCookie.indexOf(" "+cookieName+"=");
	if (ind==-1) ind=theCookie.indexOf(";"+cookieName+"=");
	if (ind==-1 || cookieName=="") return "";
	var ind1=theCookie.indexOf(";",ind+1);
	if (ind1==-1) ind1=theCookie.length; 
	return unescape(theCookie.substring(ind+cookieName.length+2,ind1));
}

function setBlankCookie(cookieName) {
	document.cookie = cookieName + '=;';
}
function cookieExists(cookieName) {
	var cookies = " " + document.cookie;
	var i = cookies.indexOf(" " + cookieName + "=");
	return (i != -1);
}

function updateFavoritesStr(arxivId, numFavorites) {
	var numFavoritesStr = document.getElementById('favorites-count-' + arxivId);
	if (numFavoritesStr) {
		var newNumFavoritesStr;
		if (numFavorites == 1) {
			newNumFavoritesStr = "(1 favorite)";
		} else {
			newNumFavoritesStr = "(" + numFavorites + " favorites)";
		}
		numFavoritesStr.innerHTML = newNumFavoritesStr;
	}
}

function login_callback(data) {
	if (data.login == 1) {
		document.getElementById('loginForm').style.display = 'none';
		document.getElementById('loggedIn').style.display = 'block';
		document.getElementById('loggedInAs').innerHTML = data.username;
		document.getElementById('welcome-message').style.display='none';	// hide the welcome message
		Dajaxice.ajax.getFavorites(loadFavorites);							// look up favorited papers
			// should also report as favorites any anonymously-favorited papers
	} else {
		var loginForm = document.getElementById('loginForm');
		var usernameEntry = loginForm.elements['username'];
		usernameEntry.style.color = "#b94a48";
		//alert(usernameEntry.style.color);
		var passwordEntry = loginForm.elements['password'];
		var clearFix = document.getElementById('loginForm-clearfix');
		clearFix.className = 'clearfix error';
		var loginFailed = document.getElementById('loginFailed');
		loginFailed.style.visibility = 'visible';
		/*alert(data.message);*/
	}
}

function loadFavorites(favs) {
		// if called by a JS function, favs is a list of arXiv IDs
		// if called back by an Ajax function, favs.arxivIds is a list of arXiv IDs
	if (favs.arxivIds) favs = favs.arxivIds;
	for (var i = 0; i < favs.length; i++) {
		var arxivId = favs[i];
		console.log('Favorite recorded for ' + arxivId);
		var cssArxivId = arxivId.replace('.','');
		$('.paper-action-star[id=' + cssArxivId + ']').addClass('paper-action-isfavorite').removeClass('paper-action-notfavorite').attr('data-original-title', 'Unfavorite').show().tooltip('hide');
		
		//var star = document.getElementById('paper-favorite-' + arxivId);
		//if (star) {
		//	star.className = 'paper-favorited';
		//	star.title = 'Unfavorite';
		//	//$('#paper-favorite-' + arxivId).twipsy('hide');
		//	/*(function (arxivId) {
		//		star.onclick = function(event) {
		//			event.stopPropagation();
		//			Dajaxice.ajax.unfavorite(unfavorite_callback, {'arxivId': arxivId});
		//		};
		//	}(arxivId));*/ // we pass a copy of the reference to arxivId
		//}
	}
}

function loadUnfavorites(unfavs) {
	if (unfavs.arxivIds) unfavs = unfavs.arxivIds;
	for (var i = 0; i < unfavs.length; i++) {
		var arxivId = unfavs[i];
		console.log('Favorite removed from ' + arxivId);
		
		var cssArxivId = arxivId.replace('.','');
		$('.paper-action-star[id=' + cssArxivId + ']').removeClass('paper-action-isfavorite').addClass('paper-action-notfavorite').attr('data-original-title', 'Favorite').tooltip('hide');
	}
}

function favorite_callback(data) {	
	loadFavorites([data.arxivId]);
	updateFavoritesStr(data.arxivId, data.numFavorites);
	
	var position = newUnfavorites.indexOf(data.arxivId);
	if (position != -1) {
		newUnfavorites.splice(position, 1);
		localStorage.newUnfavorites = JSON.stringify(newUnfavorites);
	} else if (newFavorites.indexOf(data.arxivId) == -1) {
		newFavorites.push(data.arxivId);
		localStorage.newFavorites = JSON.stringify(newFavorites);
	}
}

function unfavorite_callback(data) {
	loadUnfavorites([data.arxivId]);
	updateFavoritesStr(data.arxivId, data.numFavorites);
	
	var position = newFavorites.indexOf(data.arxivId);
	if (position != -1) {
		newFavorites.splice(position, 1);
		localStorage.newFavorites = JSON.stringify(newFavorites);
	} else if (newUnfavorites.indexOf(data.arxivId) == -1) {
		newUnfavorites.push(data.arxivId);
		localStorage.newUnfavorites = JSON.stringify(newUnfavorites);
	}
}

function toggleGooglePlusOne(jsonParam) {
	console.log('toggleGooglePlusOne');
	console.log(jsonParam);
	var arxivId = jsonParam['href'].substr(-9);
	console.log(arxivId);
	var state = jsonParam['state'];
	if (state == 'on') {
		Dajaxice.ajax.favorite(favorite_callback, {'arxivId': arxivId});
	} else {
		Dajaxice.ajax.unfavorite(unfavorite_callback, {'arxivId': arxivId});
	}
}

function getMorePapers(days) {
	Dajaxice.ajax.getMorePapers(insertNextDay, {'days': days});
}

function insertNextDay(data) {
	//alert('insertNextDay');
	var wrapper= document.createElement('div');
	//wrapper.innerHTML= '<span><div class="page-outer"><div class="interday-spacer"></div><div class="main-content"><a href="#">Hello world</a></div></div></span>';
	wrapper.innerHTML = data.newHTML;
	var div = wrapper.firstChild;
	
    var beforeMe = document.getElementById("more-papers-anchor");
	document.body.insertBefore(div, beforeMe);
	
	window.history.replaceState('object or string', 'Title', '/papers/latest/' + data.finalDays);	// replaceState updates the browser URL without adding to the page history for the back button
	
	document.getElementById('more-papers').onclick = function(event) {
		event.stopPropagation();
		getMorePapers(data.finalDays + 1);
	};
	//(function (days) {
	//document.getElementById('more-papers').onclick = function(event) {
	//	event.stopPropagation();
	//	getMorePapers(days + 1);
	//};
	//}(data.finalDays));
	
	window.scrollBy(0, 200);	// should really jump to the top of the day
	//alert('endInsert');
		
	registerPaperActions();
};

function registerPaperActions() {
	// Unregisters and reregisters the click and mouseover/out event handlers for paper actions.  
	// Unregistering them first makes it safe to call this function repeatedly, every time new 
	// papers are loaded into the DOM, without having multiple click handlers assigned.  
	$('.paper-action').not('.paper-action-isfavorite').hide();
	
	$('.paper-action-pdf').each(function() {
		var arxivId = this['id'];
		arxivId = arxivId.substring(0,4) + '.' + arxivId.substring(4,8);
		this['title'] = arxivId + '.pdf';
	});
	$('.paper-action-abstract').each(function() { this['title'] = 'arXiv'; });
	$('.paper-action-isfavorite').each(function() { this['title'] = 'Unfavorite'; });
	$('.paper-action-notfavorite').each(function() { this['title'] = 'Favorite'; });
	$('.paper-actions').tooltip({	// Enable tooltips on the new papers (note this changes the title)
		selector: 'a,div',
		placement: 'left',
		delay: 200
    });
	$('.paper').unbind('mouseout').mouseout(function() {
		$('.paper-action').not('.paper-action-isfavorite').hide();
	});			
	$('.paper').unbind('mouseover').mouseover(function() {
		$('.paper-action').not('.paper-action-isfavorite').hide();
		$('.paper-action[id=' + $(this).attr('id') + ']').show();
	});
	$('.paper').unbind('click').click(function() {
		var thisAbstractSelector = '.paper-abstract[id=' + $(this).attr('id') + ']';
		$('.paper-abstract').not(thisAbstractSelector).hide();
		$(thisAbstractSelector).toggle();
	});
	
	$('.paper-action-star').unbind('click').click(function(event) {
		//console.log('favorite toggle ' + $(this).attr('data-arxivId'));
		if ($(this).is('.paper-action-isfavorite')) {
			// by having one function, there is no need to update the click handler later
			console.log('unfaveing ' + $(this).attr('data-arxivId'));				
			Dajaxice.ajax.unfavorite(unfavorite_callback, {'arxivId': $(this).attr('data-arxivId') });				
		} else {
			console.log('faveing ' + $(this).attr('data-arxivId'));
			Dajaxice.ajax.favorite(favorite_callback, {'arxivId': $(this).attr('data-arxivId') });					
		}
		event.stopPropagation();	// return false; --- stops click event from toggling the abstract
	});
	$('.paper-action-pdf,.paper-action-abstract').unbind('click').click(function(event) {
		event.stopPropagation();	// stop click event from toggling the abstract
	});
			
	gapi.plusone.go();	// Load the GooglePlusOne buttons!
};

/******
 * Callbacks for Dajaxice testing
 ******/

var dajaxiceTesting = {
	my_js_callback: function (data) {
		alert(data.message);
	}
}
function callback_example1(data){
	alert(data.message);
}
function callback_example2(data){
	for (var i=0; i < data.numbers.length; i++) {
		alert(data.numbers[i]);
	}
}
function callback_example3(data) {
	alert(data.result);
}
function callback_example_error(data) {
	alert(data);
}
function callback_complex_example1(data) {
    alert(data.message);
}
function custom_error(){
	alert('Custom error');
}


/******
 * More scratch space
 ******/

// These arrays store the changes to favorites that a user makes before logging in, so that 
// the events can be registered when he or she logs in.  They are also stored in local 
// storage (sessionStorage) so that when the user loads the web page from the browser cache 
// (instead of from the server), the favorites are up-to-date.  
// However, it does not save the favorite counts!  So, if you unfavorite a paper (decrementing 
// the favorite count), go forward to another page and then go back, in Chrome this will 
// have the paper correctly unfavorited but with the wrong favorite count.  
// When the user clicks to fave or unfave a paper, and the confirmation comes back from the 
// server, ...
// It still doesn't work in Chrome if the user opens a new window or new tab (so loses 
// access to sessionStorage), but then loads the HTML from the cache.  I could use localStorage 
// instead, but that is persistent.  I guess I need to check whether the page is being loaded 
// from the cache or from the server, using a cookie.  
// Update: I now use localStorage so it works if the user open a new window, and the page is loaded 
// from the cache.  

var checkIfCachedWithCookies = function (uniqueKey) {
	// sets the isCached variable to true if the page is being loaded from a cache
	// works by fetching a cookie with an ID that is chosen at random by the server
	// if the cookie does not exist, then create it; page was not cached
	// if the cookie does exist, then page was cached
	isCached = cookieExists(uniqueKey);
	setBlankCookie(uniqueKey);
	//alert("isCached: " + isCached);
};

var newFavorites = [];
var newUnfavorites = [];

window.onpopstate = function(e) {
		// it is useful to know if the page is cached so Ajax data can be updated (in Safari, this is not necessary, but in Chrome it is)
	var isCached = (localStorage.cacheCheck == cacheCheckKey);
	localStorage.cacheCheck = cacheCheckKey;
	console.log('isCached= ' + isCached);
	
	if (isCached) {
		if (localStorage.newFavorites) {
			newFavorites = JSON.parse(localStorage.newFavorites);
			loadFavorites(newFavorites);
		}
		if (localStorage.newUnfavorites) {
			newUnfavorites = JSON.parse(localStorage.newUnfavorites);
			loadUnfavorites(newUnfavorites);
		}
		//alert('loading from cache');
	} else {
		localStorage.removeItem('newFavorites');
		localStorage.removeItem('newUnfavorites');
		//localStorage.clear();
	}
};

var testStateVar = "helloworld";
//window.onload = function(e) {};

