import collections
import chru

s = None

# Under no circumstances should you touch this variable.
schema = """
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

CREATE TABLE IF NOT EXISTS `api` (
    `id` INTEGER PRIMARY KEY,
    `key` TEXT NOT NULL,  -- The API key.
    `name` TEXT NOT NULL, -- The name of the key owner.
    `email` TEXT NOT NULL -- The email of the key owner.
);

"""

# Hack to make --make-config easier, OrderedDict means there's less problems.
# Reminder: change here, change in the docs!
skeleton = collections.OrderedDict()

skeleton["sql_path"] = "/path/to/chr.db"
skeleton["soft_url_cap"] = 512

skeleton["flask_host"] = "127.0.0.1"
skeleton["flask_port"] = 8080
skeleton["flask_base"] = "/"
skeleton["flask_secret_key"] = "UNIQUE_KEY"

skeleton["reserved"] = ["porn", "faggot", "sex", "nigger", "fuck",
                        "cunt", "dick", "gay", "vagina", "penis",
                        "tits", "boobs", "lesbian", "squirt",
                        "titties", "squirting", "shit", "anal"]

skeleton["captcha_public_key"] = "YOUR_PUBLIC_API_KEY"
skeleton["captcha_private_key"] = "YOUR_PRIVATE_API_KEY"

skeleton["salt_password"] = "UNIQUE_KEY"

skeleton["validate_urls"] = True
skeleton["validate_requests"] = True
skeleton["validate_regex"] = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.!&()=:;?,\-%#]*)\/?$"
skeleton["validate_fallback"] = True

skeleton["api_enabled"] = False

# Stores DB table names (easly edet ur dotobuzzes)
skeleton["_schema"] = {
    "redirects": "redirects",
    "users": "users",
    "clicks": "clicks",
    "api": "api",
    "char": "+"
}

skeleton["_slug_max"] = 32

skeleton["_version"] = chru.__version__