START TRANSACTION;

DROP PROCEDURE IF EXISTS create_report_cache_schema;
DELIMITER //
CREATE PROCEDURE `create_report_cache_schema` ()
BEGIN
	SET @tbl_version=COALESCE((
		SELECT CAST(TABLE_COMMENT AS UNSIGNED)
		FROM information_schema.tables
		WHERE table_schema=schema()
		AND table_name='report_cache'
	), 0);
	SELECT CONCAT('Updating schema in ', schema(), '.report_cache', ' (currently at version ', @tbl_version, ')...') AS '';
	IF @tbl_version < 1 THEN
		SELECT '   (1) Creating basic schema...' AS '';
		DROP TABLE IF EXISTS report_cache;
		CREATE TABLE report_cache (
			dbname varchar(64) NOT NULL default '',
			report_key varchar(64) NOT NULL default '',
			last_run int(11) default NULL,
			last_start int(11) default NULL,
			result longblob,
			PRIMARY KEY  (`dbname`,`report_key`)
		) ENGINE=InnoDB COMMENT '1' DEFAULT CHARSET=latin1;
	END IF;

	IF @tbl_version < 2 THEN
		SELECT '   (2) Add duration column...' AS '';
		ALTER TABLE report_cache
			ADD COLUMN last_run_duration int(11) default NULL;
		ALTER TABLE report_cache COMMENT '2';
	END IF;
END//

DELIMITER ;

CALL create_report_cache_schema();
DROP PROCEDURE create_report_cache_schema;
