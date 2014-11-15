/* Copyright (c) 2008 River Tarnell <river@wikimedia.org>. */
/*
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely. This software is provided 'as-is', without any express or implied
 * warranty.
 */
/* $Id: reports.js 54 2008-09-17 23:49:25Z river $ */
   
function format_wiki(ul, item) {
    li = $('<li>').attr("data-value", item[0]);
    li.append("<span class='wikilist_ac_domain'>").append(item.value);
    li.append("<br>");
    li.append("<span class='wikilist_ac_dbname'>").append(item.dbname);
    return li.appendTo(ul);
}

function report_setup() {
	$("input.wikilist").autocomplete(
		{ source: rep_docroot + "/wikilist.fcgi",
		  autoFill: false, 
		  matchSubset: false}
	).autocomplete('instance')._renderItem = format_wiki;

	/*
	 * We can only auto-complete wiki-specific forms if a database has been set.
	 */
	if (typeof(rep_dbname) != 'undefined') {
		$("input.username").autocomplete(
			{	source: rep_docroot + "/userlist.fcgi",
				autoFill: true, 
				matchCase: true, 
				matchSubset: false, 
				extraParams: { dbname: rep_dbname } 
			});
	}

	$('#lang').chosen({search_contains: true})
}

$(document).ready(report_setup);
