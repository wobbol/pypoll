CREATE TABLE users (
    id     INTEGER NOT NULL PRIMARY KEY ASC,
    date   INTEGER NOT NULL,
    cookie TEXT    NOT NULL,
    ip     TEXT    NOT NULL
);
CREATE TABLE radio_question_answers (
    id     INTEGER NOT NULL PRIMARY KEY ASC,
    answer TEXT    NOT NULL
);
CREATE TABLE radio_questions (
    id         INTEGER NOT NULL PRIMARY KEY ASC,
    question      TEXT NOT NULL,
    answer1_id INTEGER NOT NULL,
    answer2_id INTEGER NOT NULL,
    answer3_id INTEGER NOT NULL,
    answer4_id INTEGER NOT NULL,
    FOREIGN KEY (answer1_id)
        REFERENCES radio_question_answers(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    FOREIGN KEY (answer2_id)
        REFERENCES radio_question_answers(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    FOREIGN KEY (answer3_id)
        REFERENCES radio_question_answers(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    FOREIGN KEY (answer4_id)
        REFERENCES radio_question_answers(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);
CREATE TABLE radio_answers (
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
