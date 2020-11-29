CREATE TABLE users (
    id     INTEGER NOT NULL PRIMARY KEY ASC,
    date   INTEGER NOT NULL,
    cookie TEXT    NOT NULL,
    ip     TEXT    NOT NULL
);
CREATE TABLE poll (
    id    INTEGER NOT NULL PRIMARY KEY ASC,
    name  TEXT    NOT NULL,
    token TEXT    NOT NULL
);
CREATE TABLE radio_questions (
    id       INTEGER NOT NULL PRIMARY KEY ASC,
    question TEXT NOT NULL,
    poll_id TEXT NOT NULL,
    FOREIGN KEY (poll_id)
        REFERENCES poll(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);
CREATE TABLE radio_question_answers (
    id                INTEGER NOT NULL PRIMARY KEY ASC,
    radio_question_id INTEGER NOT NULL,
    answer            TEXT    NOT NULL,
    FOREIGN KEY (radio_question_id)
        REFERENCES radio_questions(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);
CREATE TABLE user_answers (
    id          INTEGER NOT NULL PRIMARY KEY ASC,
    user_id     INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer_id   INTEGER NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    FOREIGN KEY (question_id)
        REFERENCES radio_questions(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    FOREIGN KEY (answer_id)
        REFERENCES radio_question_answers(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);
