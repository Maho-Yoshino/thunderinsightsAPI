DROP DATABASE IF EXISTS `wt_api_cache`;
CREATE DATABASE "wt_api_cache" DEFAULT CHARACTER SET utf8mb4;

USE `wt_api_cache`;

CREATE TABLE `clans` (
	`id` int PRIMARY KEY NOT NULL,
	`name` varchar(255) NOT NULL,
	`tag` varchar(255) NOT NULL,
	`type` tinyint NOT NULL
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

ALTER TABLE `user` ADD FOREIGN KEY (`clan_id`) REFERENCES `clan` (`id`);
