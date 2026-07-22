PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
INSERT INTO messages VALUES(1,'user','Lexi, confirm the core is alive.','2026-05-12T22:20:24.975918');
INSERT INTO messages VALUES(2,'assistant',replace('Lexi.AI core is running locally. I do not see an API key yet, so I am in offline scaffold mode.\n\nYou said: Lexi, confirm the core is alive.\n\nCommands you can use now:\n- /remember your note here\n- /recall\n- /health\n\nTo activate full AI replies, add your OpenAI API key to the .env file.','\n',char(10)),'2026-05-12T22:20:24.977632');
INSERT INTO messages VALUES(3,'user','/remember Build Lexi.AI Mac Core first, then Android companion, then dashboard.','2026-05-12T22:22:13.075893');
INSERT INTO messages VALUES(4,'assistant','Memory saved: Build Lexi.AI Mac Core first, then Android companion, then dashboard.','2026-05-12T22:22:13.080754');
INSERT INTO messages VALUES(5,'user','/recall','2026-05-12T22:23:01.004425');
INSERT INTO messages VALUES(6,'assistant',replace('Here is what I have stored:\n\n- [note] Build Lexi.AI Mac Core first, then Android companion, then dashboard. (2026-05-12T22:22:13.078544)','\n',char(10)),'2026-05-12T22:23:01.006609');
CREATE TABLE memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
INSERT INTO memories VALUES(1,'note','Build Lexi.AI Mac Core first, then Android companion, then dashboard.','2026-05-12T22:22:13.078544');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('messages',6);
INSERT INTO sqlite_sequence VALUES('memories',1);
COMMIT;
