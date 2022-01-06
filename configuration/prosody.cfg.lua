-- Prosody Example Configuration File
--
-- If it wasn't already obvious, -- starts a comment, and all 
-- text after it on a line is ignored by Prosody.
--
-- The config is split into sections, a global section, and one 
-- for each defined host that we serve. You can add as many host 
-- sections as you like.
--
-- Lists are written
-- _ = { "like", "this", "one" } 
-- Lists can also be of { 1, 2, 3 } numbers, etc. 
-- Either commas, or semi-colons; may be used
-- as separators.
--
-- A table is a list of values, except each value has a name. An 
-- example would be:
--
-- examlpe_ssl = { key = "localhost.key", certificate = "localhost.crt" }
--
-- Whitespace (that is tabs, spaces, line breaks) is mostly insignificant, so 
-- can 
-- be placed anywhere
-- that   you deem fitting.
--
-- Tip: You can check that the syntax of this file is correct
-- when you have finished by running this command:
--     prosodyctl check config
-- If there are any errors, it will let you know what and where
-- they are, otherwise it will keep quiet.
--
-- The only thing left to do is rename this file to remove the .dist ending, and fill in the
-- blanks. Good luck, and happy Jabbering!


---------- Server-wide settings ----------
-- Settings in this section apply to the whole server and are the default settings
-- for any virtual hosts

-- This is a (by default, empty) list of accounts that are admins
-- for the server. Note that you must create the accounts separately
-- (see https://prosody.im/doc/creating_accounts for info)
-- Example: admins = { "user1@example.com", "user2@example.net" }
admins = {"Neo@fl"}

-- Enable use of libevent for better performance under high load
-- For more information see: https://prosody.im/doc/libevent
--use_libevent = true

-- Prosody will always look in its source directory for modules, but
-- this option allows you to specify additional locations where Prosody
-- will look for modules first. For community modules, see https://modules.prosody.im/
--plugin_paths = {}

-- This is the list of modules Prosody will load on startup.
-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.
-- Documentation for bundled modules can be found at: https://prosody.im/doc/modules
modules_enabled = {

    -- Generally required
        "roster"; -- Allow users to have a roster. Recommended ;)
        "saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.
        "tls"; -- Add support for secure TLS on c2s/s2s connections
        "dialback"; -- s2s dialback support
        "disco"; -- Service discovery

    -- Not essential, but recommended
        "carbons"; -- Keep multiple clients in sync
        "pep"; -- Enables users to publish their avatar, mood, activity, playing music and more
        "private"; -- Private XML storage (for room bookmarks, etc.)
        "blocklist"; -- Allow users to block communications with other users
        "vcard4"; -- User profiles (stored in PEP)
        "vcard_legacy"; -- Conversion between legacy vCard and PEP Avatar, vcard

    -- Nice to have
        "version"; -- Replies to server version requests
        "uptime"; -- Report how long server has been running
        "time"; -- Let others know the time here on this server
        "ping"; -- Replies to XMPP pings with pongs
        "register"; -- Allow users to register on this server using a client and change passwords
        --"mam"; -- Store messages in an archive and allow users to access it
        --"csi_simple"; -- Simple Mobile optimizations

    -- Admin interfaces
        "admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands
        --"admin_telnet"; -- Opens telnet console interface on localhost port 5582

    -- HTTP modules
        --"bosh"; -- Enable BOSH clients, aka "Jabber over HTTP"
        --"websocket"; -- XMPP over WebSockets
        --"http_files"; -- Serve static files from a directory over HTTP

    -- Other specific functionality
        --"limits"; -- Enable bandwidth limiting for XMPP connections
        --"groups"; -- Shared roster support
        --"server_contact_info"; -- Publish contact information for this service
        --"announce"; -- Send announcement to all online users
        --"welcome"; -- Welcome users who register accounts
        --"watchregistrations"; -- Alert admins of registrations
        --"motd"; -- Send a message to users when they log in
        --"legacyauth"; -- Legacy authentication. Only used by some old clients and bots.
        --"proxy65"; -- Enables a file transfer proxy service which clients behind NAT can use
}

-- These modules are auto-loaded, but should you want
-- to disable them then uncomment them here:
modules_disabled = {
    -- "offline"; -- Store offline messages
    -- "c2s"; -- Handle client connections
    -- "s2s"; -- Handle server-to-server connections
    -- "posix"; -- POSIX functionality, sends server to background, enables syslog, etc.
}

-- Disable account creation by default, for security
-- For more information see https://prosody.im/doc/creating_accounts
allow_registration = true


c2s_require_encryption = true

archive_expires_after = "1w" -- Remove archived messages after 1 week

log = {
    debug = "prosody.log"; -- Change 'info' to 'debug' for verbose logging
    error = "prosody.err";
    "*syslog"; -- Uncomment this for logging to syslog
    "*console"; -- Log to the console, useful for debugging with daemonize=false
}

certificates = "certs"
VirtualHost "jabber"
