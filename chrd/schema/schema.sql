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
	`delete` varchar(64) NOT NULL, -- String to delete. /slug/delete/<`delete`>
	`user` INTEGER NOT NULL DEFAULT '0', -- Which user made this? 0 means non-logged in.
	`ip` varchar(15) NOT NULL -- raw ip of the submitter.
);

CREATE TABLE IF NOT EXISTS `clicks` (
	`id` INTEGER PRIMARY KEY,
	`url` INTEGER NOT NULL,    -- id from redirect row
	`ip` varchar(15) NOT NULL, -- raw ip in form of 'W{1,3}.X{1,3}.Y{1,3}.Z{1,3}'
	`time` INTEGER NOT NULL,   -- int(time.time()) of hit
	`agent` TEXT NOT NULL,     -- Their user agent. Trimmed to a max of 256
	`agent_platform` TEXT NOT NULL, -- These are all based off of the
	`agent_browser` TEXT NOT NULL,  -- flask request.user_agent variable.
	`agent_version` TEXT NOT NULL,  -- It has the platform (Win, Mac), browser (Firefox, Safari)
	`agent_language` TEXT NOT NULL  -- aswell as version and language.
);