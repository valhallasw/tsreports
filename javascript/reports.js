/* Copyright (c) 2008 River Tarnell <river@wikimedia.org>. */
/*
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely. This software is provided 'as-is', without any express or implied
 * warranty.
 */
/* $Id: reports.js 54 2008-09-17 23:49:25Z river $ */
   
function format_wiki(row) {
	return "<span class='wikilist_ac_domain'>" + row[0] + "</span>"
		+ "<br /><span class='wikilist_ac_dbname'>" + row[1] + "</span>";
}

function report_setup() {
	$("input.wikilist").autocomplete(rep_docroot + "/wikilist.fcgi", 
		{ autoFill: false, 
		  matchSubset: false,
		  formatItem: format_wiki });

	/*
	 * We can only auto-complete wiki-specific forms if a database has been set.
	 */
	if (typeof(rep_dbname) != 'undefined') {
		$("input.username").autocomplete(rep_docroot + "/userlist.fcgi",
			{	autoFill: true, 
				matchCase: true, 
				matchSubset: false, 
				extraParams: { dbname: rep_dbname } 
			});
	}
}

$(document).ready(report_setup);
