matches.db: createDb.sql
	sqlite3 matches.db <createDb.sql

error.log:
	- mkdir log
	- touch log/error.log