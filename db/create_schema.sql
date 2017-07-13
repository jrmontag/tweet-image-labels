-- create db 
CREATE DATABASE image_labels;
USE image_labels;

-- always start fresh 
DROP TABLE IF EXISTS classifications; 
DROP TABLE IF EXISTS labels;

-- create schemas
CREATE TABLE classifications(
    id BIGINT(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tweet_id BIGINT(20) NOT NULL,
    link VARCHAR(1024) NOT NULL,
    keyword1 VARCHAR(255),
    score1 DOUBLE,
    keyword2 VARCHAR(255),
    score2 DOUBLE,
    keyword3 VARCHAR(255),
    score3 DOUBLE,
    keyword4 VARCHAR(255),
    score4 DOUBLE,
    keyword5 VARCHAR(255),
    score5 DOUBLE,
    label_id BIGINT(20)
);

CREATE TABLE labels(
    id BIGINT(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
 
-- load fixed accuracy labels  
INSERT INTO labels(name) VALUES ('top1'), ('top5'), ('None'); 

-- create user (for app use) + credentials
GRANT ALL ON image_labels.* TO 'imgapp'@'%' IDENTIFIED BY 'apassword';

-- create a test table (useful for debugging) 
-- CREATE TABLE test_classifications AS SELECT * FROM classifications LIMIT 30;

