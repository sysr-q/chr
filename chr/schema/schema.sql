-- THIS IS FOR sqlite3, NOT MySQL, SO DON'T TRY TO EVEN USE IT, BRO.

CREATE TABLE IF NOT EXISTS `users` (
	`id` INTEGER PRIMARY KEY,
	`login` varchar(32) NOT NULL,    -- Login name (lower case)
	`display` varchar(32) NOT NULL,  -- Displayed login name
	`password` varchar(64) NOT NULL, -- sha256() hash of (salt + login.lower() + password + salt)
	`email` varchar(64) NOT NULL,
	`admin` tinyint(1) NOT NULL DEFAULT '0'
);


-- To calculate hits: 'SELECT `id` FROM `clicks` WHERE `url` = <redirect_id>', then count.
CREATE TABLE IF NOT EXISTS `redirects` (
	`id` INTEGER PRIMARY KEY,
	`long` TEXT NOT NULL,
	`short` TEXT NOT NULL, -- Added afterwards. This is the base62 encoding for the row id.
	`user` INTEGER NOT NULL DEFAULT '0' -- Which user made this? 0 means non-logged in.
);

CREATE TABLE IF NOT EXISTS `clicks` (
	`id` INTEGER PRIMARY KEY,
	`url` INTEGER NOT NULL,    -- id from redirect row
	`ip` varchar(15) NOT NULL, -- raw ip in form of 'W{1,3}.X{1,3}.Y{1,3}.Z{1,3}'
	`time` INTEGER NOT NULL    -- int(time.time()) of hit
)