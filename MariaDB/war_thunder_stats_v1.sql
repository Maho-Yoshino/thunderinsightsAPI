DROP DATABASE IF EXISTS `war_thunder_stats_v1`;

CREATE DATABASE `war_thunder_stats_v1` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

USE war_thunder_stats_v1;



CREATE TABLE `language` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `language` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `unit_class` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `class` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `unit_class_translation` (
  `class_id` smallint NOT NULL,
  `language_id` smallint NOT NULL,
  `translation` varchar(255) DEFAULT null,
  PRIMARY KEY (`class_id`, `language_id`)
);

CREATE TABLE `unit_tag` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `unit_tag_translation` (
  `tag_id` smallint NOT NULL,
  `language_id` smallint NOT NULL,
  `translation` varchar(255) DEFAULT null,
  PRIMARY KEY (`tag_id`, `language_id`)
);

CREATE TABLE `country` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `country_translation` (
  `country_id` smallint NOT NULL,
  `language_id` smallint NOT NULL,
  `translation` varchar(255) DEFAULT null,
  PRIMARY KEY (`country_id`, `language_id`)
);

CREATE TABLE `unit_type` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `type` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `tier` (
  `id` smallint PRIMARY KEY NOT NULL,
  `tier` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `battlerating` (
  `id` smallint PRIMARY KEY NOT NULL,
  `battlerating` decimal(4,1) UNIQUE DEFAULT null
);

CREATE TABLE `unit_value` (
  `id` mediumint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `value` int UNIQUE DEFAULT null
);

CREATE TABLE `unit` (
  `id` mediumint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE DEFAULT null,
  `country_id` smallint,
  `type_id` smallint,
  `tier_id` smallint,
  `experience_id` mediumint,
  `cost_id` mediumint,
  `gold_cost_id` mediumint,
  `operator_country_id` smallint,
  `premium` tinyint DEFAULT 0,
  `gift` tinyint DEFAULT 0,
  `event` tinyint DEFAULT 0,
  `clan` tinyint DEFAULT 0,
  `release_date` datetime DEFAULT null,
  `include_in_search` tinyint
);

CREATE TABLE `unit_tag_correlation` (
  `unit_id` mediumint NOT NULL,
  `unit_tag_id` smallint NOT NULL,
  PRIMARY KEY (`unit_id`, `unit_tag_id`)
);

CREATE TABLE `unit_translation` (
  `unit_id` mediumint NOT NULL,
  `language_id` smallint NOT NULL,
  `shop_name` varchar(255) DEFAULT null,
  `full_name` varchar(255) DEFAULT null,
  `short_name` varchar(255) DEFAULT null,
  `compressed_name` varchar(255) DEFAULT null,
  PRIMARY KEY (`unit_id`, `language_id`)
);

CREATE TABLE `gamemode` (
  `id` tinyint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `battlerating_correlation` (
  `unit_id` mediumint NOT NULL,
  `gamemode_id` tinyint NOT NULL,
  `battlerating_id` smallint DEFAULT null,
  PRIMARY KEY (`unit_id`, `gamemode_id`)
);

CREATE TABLE `modification_status` (
  `id` tinyint PRIMARY KEY NOT NULL,
  `title` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `game_type` (
  `id` tinyint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE DEFAULT null
);

CREATE TABLE `title` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `title_translation` (
  `title_id` smallint NOT NULL,
  `language_id` smallint NOT NULL,
  `translation` varchar(255) DEFAULT null,
  `description` varchar(255) DEFAULT null,
  PRIMARY KEY (`title_id`, `language_id`)
);

CREATE TABLE `rank` (
  `rank` smallint PRIMARY KEY NOT NULL,
  `experience` int NOT NULL
);

CREATE TABLE `clan` (
  `id` int PRIMARY KEY NOT NULL,
  `name` varchar(255) NOT NULL,
  `tag` varchar(255) NOT NULL,
  `type` tinyint NOT NULL
);

CREATE TABLE `clan_role` (
  `id` tinyint PRIMARY KEY NOT NULL,
  `name` varchar(255) DEFAULT null
);

CREATE TABLE `icon` (
  `id` smallint PRIMARY KEY NOT NULL,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `frame` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `background` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `showcase` (
  `id` smallint PRIMARY KEY NOT NULL,
  `type` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `penalty_type` (
  `id` smallint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `status` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `user` (
  `id` bigint PRIMARY KEY NOT NULL,
  `clan_id` int DEFAULT null,
  `nickname` varchar(255) DEFAULT null,
  `clan_member_role_id` tinyint DEFAULT null,
  `last_day` datetime DEFAULT null,
  `register_day` datetime DEFAULT null,
  `selected_title_id` smallint DEFAULT null,
  `icon_id` smallint DEFAULT null,
  `frame_id` smallint DEFAULT null,
  `background_id` smallint DEFAULT null,
  `showcase_type_id` smallint DEFAULT null,
  `datetime` datetime DEFAULT null
);

CREATE TABLE `penalty_correlation` (
  `penalty_id` smallint NOT NULL,
  `user_id` bigint NOT NULL,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`penalty_id`, `user_id`)
);

CREATE TABLE `title_correlation` (
  `user_id` bigint NOT NULL,
  `title_id` smallint NOT NULL,
  PRIMARY KEY (`user_id`, `title_id`)
);

CREATE TABLE `general_stat` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `experience` bigint DEFAULT null,
  `experience_converted` bigint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`)
);

CREATE TABLE `unlock_type` (
  `id` mediumint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `type` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE `unlock` (
  `id` mediumint PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL,
  `type_id` mediumint NOT NULL
);

CREATE TABLE `unlock_translation` (
  `unlock_id` mediumint NOT NULL,
  `language_id` smallint NOT NULL,
  `translation` varchar(255) DEFAULT null,
  `description` varchar(255) DEFAULT null,
  PRIMARY KEY (`unlock_id`, `language_id`)
);

CREATE TABLE `unlock_correlation` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `unlock_id` mediumint NOT NULL,
  `stage` tinyint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `unlock_id`)
);

CREATE TABLE `unit_stat` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `unit_id` mediumint NOT NULL,
  `gamemode_id` tinyint NOT NULL,
  `spawns` mediumint DEFAULT null,
  `deaths` mediumint DEFAULT null,
  `experience_earned` int DEFAULT null,
  `silverLions_earned` bigint DEFAULT null,
  `ground_kills` mediumint DEFAULT null,
  `air_kills` mediumint DEFAULT null,
  `naval_kills` mediumint DEFAULT null,
  `was_in_lineup` mediumint DEFAULT null,
  `defeats` mediumint DEFAULT null,
  `victories` mediumint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `unit_id`, `gamemode_id`)
);

CREATE TABLE `user_modification_status` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `unit_id` mediumint NOT NULL,
  `modification_status_id` tinyint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `unit_id`)
);

CREATE TABLE `summary_stats_game` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `game_type_id` tinyint NOT NULL,
  `gamemode_id` tinyint NOT NULL,
  `missions_completed` mediumint DEFAULT null,
  `victories` mediumint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `game_type_id`, `gamemode_id`)
);

CREATE TABLE `summary_stat` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `game_type_id` tinyint NOT NULL,
  `gamemode_id` tinyint NOT NULL,
  `unit_class_id` smallint NOT NULL,
  `time_played` int DEFAULT null,
  `air_kills` mediumint DEFAULT null,
  `ground_kills` mediumint DEFAULT null,
  `naval_kills` mediumint DEFAULT null,
  `spawns` mediumint DEFAULT null,
  `air_kills_ai` mediumint DEFAULT null,
  `ground_kills_ai` mediumint DEFAULT null,
  `naval_kills_ai` mediumint DEFAULT null,
  `air_kills_bot` mediumint DEFAULT null,
  `ground_kills_bot` mediumint DEFAULT null,
  `naval_kills_bot` mediumint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `game_type_id`, `gamemode_id`, `unit_class_id`)
);

CREATE TABLE `era` (
  `datetime` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `country_id` smallint NOT NULL,
  `unit_type_id` smallint NOT NULL,
  `era` smallint DEFAULT null,
  PRIMARY KEY (`datetime`, `user_id`, `country_id`, `unit_type_id`)
);

CREATE TABLE `update` (
  `id` smallint PRIMARY KEY NOT NULL,
  `title` varchar(255) DEFAULT null,
  `version` varchar(255) UNIQUE DEFAULT null,
  `date` datetime DEFAULT null,
  `eol_date` datetime DEFAULT null,
  `stat_refresh_enabled` tinyint DEFAULT null
);

CREATE TABLE `unit_stats_by_update` (
  `unit_id` mediumint NOT NULL,
  `update_id` smallint NOT NULL,
  `gamemode_id` tinyint NOT NULL,
  `played_by_unique_users` int DEFAULT null,
  `owned_by_unique_users` int DEFAULT null,
  `spawns` bigint DEFAULT null,
  `deaths` bigint DEFAULT null,
  `experience_earned` bigint DEFAULT null,
  `silver_lions_earned` bigint DEFAULT null,
  `ground_kills` bigint DEFAULT null,
  `air_kills` bigint DEFAULT null,
  `naval_kills` bigint DEFAULT null,
  `was_in_lineup` bigint DEFAULT null,
  `defeats` bigint DEFAULT null,
  `victories` bigint DEFAULT null,
  PRIMARY KEY (`unit_id`, `update_id`, `gamemode_id`)
);

ALTER TABLE `unit_class_translation` ADD FOREIGN KEY (`class_id`) REFERENCES `unit_class` (`id`);

ALTER TABLE `unit_class_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `unit_tag_translation` ADD FOREIGN KEY (`tag_id`) REFERENCES `unit_tag` (`id`);

ALTER TABLE `unit_tag_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `country_translation` ADD FOREIGN KEY (`country_id`) REFERENCES `country` (`id`);

ALTER TABLE `country_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`country_id`) REFERENCES `country` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`type_id`) REFERENCES `unit_type` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`tier_id`) REFERENCES `tier` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`experience_id`) REFERENCES `unit_value` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`cost_id`) REFERENCES `unit_value` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`gold_cost_id`) REFERENCES `unit_value` (`id`);

ALTER TABLE `unit` ADD FOREIGN KEY (`operator_country_id`) REFERENCES `country` (`id`);

ALTER TABLE `unit_tag_correlation` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `unit_tag_correlation` ADD FOREIGN KEY (`unit_tag_id`) REFERENCES `unit_tag` (`id`);

ALTER TABLE `unit_translation` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `unit_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `battlerating_correlation` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `battlerating_correlation` ADD FOREIGN KEY (`gamemode_id`) REFERENCES `gamemode` (`id`);

ALTER TABLE `battlerating_correlation` ADD FOREIGN KEY (`battlerating_id`) REFERENCES `battlerating` (`id`);

ALTER TABLE `title_translation` ADD FOREIGN KEY (`title_id`) REFERENCES `title` (`id`);

ALTER TABLE `title_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`clan_id`) REFERENCES `clan` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`clan_member_role_id`) REFERENCES `clan_role` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`selected_title_id`) REFERENCES `title` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`icon_id`) REFERENCES `icon` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`frame_id`) REFERENCES `frame` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`background_id`) REFERENCES `background` (`id`);

ALTER TABLE `user` ADD FOREIGN KEY (`showcase_type_id`) REFERENCES `showcase` (`id`);

ALTER TABLE `penalty_correlation` ADD FOREIGN KEY (`penalty_id`) REFERENCES `penalty_type` (`id`);

ALTER TABLE `penalty_correlation` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `title_correlation` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `title_correlation` ADD FOREIGN KEY (`title_id`) REFERENCES `title` (`id`);

ALTER TABLE `general_stat` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `unlock` ADD FOREIGN KEY (`type_id`) REFERENCES `unlock_type` (`id`);

ALTER TABLE `unlock_translation` ADD FOREIGN KEY (`unlock_id`) REFERENCES `unlock` (`id`);

ALTER TABLE `unlock_translation` ADD FOREIGN KEY (`language_id`) REFERENCES `language` (`id`);

ALTER TABLE `unlock_correlation` ADD FOREIGN KEY (`unlock_id`) REFERENCES `unlock` (`id`);

ALTER TABLE `unlock_correlation` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `unit_stat` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `unit_stat` ADD FOREIGN KEY (`gamemode_id`) REFERENCES `gamemode` (`id`);

ALTER TABLE `unit_stat` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `user_modification_status` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `user_modification_status` ADD FOREIGN KEY (`modification_status_id`) REFERENCES `modification_status` (`id`);

ALTER TABLE `user_modification_status` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `summary_stats_game` ADD FOREIGN KEY (`game_type_id`) REFERENCES `game_type` (`id`);

ALTER TABLE `summary_stats_game` ADD FOREIGN KEY (`gamemode_id`) REFERENCES `gamemode` (`id`);

ALTER TABLE `summary_stats_game` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `summary_stat` ADD FOREIGN KEY (`game_type_id`) REFERENCES `game_type` (`id`);

ALTER TABLE `summary_stat` ADD FOREIGN KEY (`gamemode_id`) REFERENCES `gamemode` (`id`);

ALTER TABLE `summary_stat` ADD FOREIGN KEY (`unit_class_id`) REFERENCES `unit_class` (`id`);

ALTER TABLE `summary_stat` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `era` ADD FOREIGN KEY (`country_id`) REFERENCES `country` (`id`);

ALTER TABLE `era` ADD FOREIGN KEY (`unit_type_id`) REFERENCES `unit_type` (`id`);

ALTER TABLE `era` ADD FOREIGN KEY (`era`) REFERENCES `tier` (`id`);

ALTER TABLE `era` ADD FOREIGN KEY (`datetime`, `user_id`) REFERENCES `general_stat` (`datetime`, `user_id`);

ALTER TABLE `unit_stats_by_update` ADD FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`);

ALTER TABLE `unit_stats_by_update` ADD FOREIGN KEY (`update_id`) REFERENCES `update` (`id`);

ALTER TABLE `unit_stats_by_update` ADD FOREIGN KEY (`gamemode_id`) REFERENCES `gamemode` (`id`);













INSERT INTO `war_thunder_stats_v1`.`title` (`name`) VALUES ("");

INSERT INTO `war_thunder_stats_v1`.`clan_role` (`id`,`name`) VALUES (1,'Commander');
INSERT INTO `war_thunder_stats_v1`.`clan_role` (`id`,`name`) VALUES (2,'Officer');
INSERT INTO `war_thunder_stats_v1`.`clan_role` (`id`,`name`) VALUES (3,'Private');
INSERT INTO `war_thunder_stats_v1`.`clan_role` (`id`,`name`) VALUES (5,'Deputy');
INSERT INTO `war_thunder_stats_v1`.`clan_role` (`id`,`name`) VALUES (6,'Sergeant');

INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (0,1.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (1,1.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (2,1.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (3,2.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (4,2.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (5,2.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (6,3.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (7,3.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (8,3.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (9,4.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (10,4.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (11,4.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (12,5.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (13,5.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (14,5.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (15,6.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (16,6.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (17,6.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (18,7.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (19,7.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (20,7.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (21,8.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (22,8.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (23,8.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (24,9.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (25,9.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (26,9.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (27,10.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (28,10.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (29,10.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (30,11.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (31,11.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (32,11.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (33,12.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (34,12.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (35,12.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (36,13.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (37,13.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (38,13.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (39,14.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (40,14.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (41,14.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (42,15.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (43,15.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (44,15.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (45,16.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (46,16.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (47,16.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (48,17.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (49,17.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (50,17.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (51,18.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (52,18.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (53,18.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (54,19.0);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (55,19.3);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (56,19.7);
INSERT INTO `war_thunder_stats_v1`.`battlerating` (`id`,`battlerating`) VALUES (57,20.0);

INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (1,'I');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (2,'II');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (3,'III');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (4,'IV');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (5,'V');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (6,'VI');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (7,'VII');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (8,'VIII');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (9,'IX');
INSERT INTO `war_thunder_stats_v1`.`tier` (`id`,`tier`) VALUES (10,'X');

INSERT INTO `war_thunder_stats_v1`.`modification_status` (`id`,`title`) VALUES (0,'0-49% researched');
INSERT INTO `war_thunder_stats_v1`.`modification_status` (`id`,`title`) VALUES (1,'50-99% researched');
INSERT INTO `war_thunder_stats_v1`.`modification_status` (`id`,`title`) VALUES (2,'Spaded');