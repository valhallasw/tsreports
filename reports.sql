DROP TABLE IF EXISTS report_cache;
CREATE TABLE report_cache (
	dbname varchar(64) NOT NULL default '',
	report_key varchar(64) NOT NULL default '',
	last_run int(11) default NULL,
	last_start int(11) default NULL,
	result longblob,
	PRIMARY KEY  (`dbname`,`report_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
