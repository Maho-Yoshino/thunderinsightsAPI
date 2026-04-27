Use WarThunderStats;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE `WarThunderStats`.`Battlerating`, `WarThunderStats`.`BattleratingCorrelations`, `WarThunderStats`.`ClanRoles`, `WarThunderStats`.`Clans`, `WarThunderStats`.`Country`, `WarThunderStats`.`Gamemode`, `WarThunderStats`.`GameType`, `WarThunderStats`.`GeneralStats`, `WarThunderStats`.`Icons`, `WarThunderStats`.`Languages`, `WarThunderStats`.`ModificationStatus`, `WarThunderStats`.`ModificationStatusPerUser`, `WarThunderStats`.`SummaryStats`, `WarThunderStats`.`SummaryStatsGames`, `WarThunderStats`.`Tier`, `WarThunderStats`.`TitleCorrelations`, `WarThunderStats`.`Titles`, `WarThunderStats`.`Users`, `WarThunderStats`.`VehicleClass`, `WarThunderStats`.`VehicleCost`, `WarThunderStats`.`VehicleExperienceRequirement`, `WarThunderStats`.`VehicleInformation`, `WarThunderStats`.`VehicleNames`, `WarThunderStats`.`VehicleStats`, `WarThunderStats`.`VehicleTagCorrelations`, `WarThunderStats`.`VehicleTags`, `WarThunderStats`.`VehicleType`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `Languages` (
  `LanguageID` tinyint(4) NOT NULL AUTO_INCREMENT,
  `Language` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`LanguageID`),
  UNIQUE KEY `Language_UNIQUE` (`Language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleClass` (
  `VehicleClassID` tinyint(4) NOT NULL AUTO_INCREMENT,
  `VehicleClassName` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`VehicleClassID`),
  UNIQUE KEY `VehicleClassName_UNIQUE` (`VehicleClassName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleTags` (
  `VehicleTagID` smallint(8) NOT NULL AUTO_INCREMENT,
  `VehicleTagName` varchar(128) DEFAULT NULL,
  `VehicleTagNameHumanReadable` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`VehicleTagID`),
  UNIQUE KEY `VehicleTagName_UNIQUE` (`VehicleTagName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Country` (
  `CountryID` smallint(8) NOT NULL AUTO_INCREMENT,
  `NationName` varchar(128) DEFAULT NULL,
  `NationNameHumanReadable` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`CountryID`),
  UNIQUE KEY `NationName_UNIQUE` (`NationNameHumanReadable`),
  UNIQUE KEY `NationTitle_UNIQUE` (`NationName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleType` (
  `VehicleTypeID` tinyint(4) NOT NULL AUTO_INCREMENT,
  `VehicleTypeName` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`VehicleTypeID`),
  UNIQUE KEY `VehicleTypeName_UNIQUE` (`VehicleTypeName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Tier` (
  `TierID` tinyint(4) NOT NULL,
  `TierRoman` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`TierID`),
  UNIQUE KEY `TierRoman_UNIQUE` (`TierRoman`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Battlerating` (
  `BatleratingID` tinyint(4) NOT NULL,
  `BattleratingValue` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`BatleratingID`),
  UNIQUE KEY `BattleratingValue_UNIQUE` (`BattleratingValue`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleCost` (
  `VehicleCostID` int(16) NOT NULL AUTO_INCREMENT,
  `VehicleCost` int(32) DEFAULT NULL,
  PRIMARY KEY (`VehicleCostID`),
  UNIQUE KEY `VehicleCost_UNIQUE` (`VehicleCost`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleExperienceRequirement` (
  `VehicleExperienceID` int(16) NOT NULL AUTO_INCREMENT,
  `VehicleExperience` int(24) DEFAULT NULL,
  PRIMARY KEY (`VehicleExperienceID`),
  UNIQUE KEY `VehicleExperience_UNIQUE` (`VehicleExperience`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleInformation` (
  `VehicleID` int(32) NOT NULL AUTO_INCREMENT,
  `VehicleName` varchar(128) DEFAULT NULL,
  `VehicleCountryID` smallint(8) DEFAULT NULL,
  `VehicleTypeID` tinyint(4) DEFAULT NULL,
  `VehicleTierID` tinyint(4) DEFAULT NULL,
  `VehicleExperienceID` int(16) DEFAULT NULL,
  `VehicleCostID` int(16) DEFAULT NULL,
  `VehicleCostGoldID` int(16) DEFAULT NULL,
  `OperatorCountryID` smallint(8) DEFAULT NULL,
  `Premium` tinyint(4) DEFAULT NULL,
  `Gift` tinyint(4) DEFAULT NULL,
  `Event` tinyint(4) DEFAULT NULL,
  `Clan` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`VehicleID`),
  UNIQUE KEY `VehicleName_UNIQUE` (`VehicleName`),
  KEY `VehicleCountryId_idx` (`VehicleCountryID`),
  KEY `VehicleTypeId_idx` (`VehicleTypeID`),
  KEY `VehicleTierId_idx` (`VehicleTierID`),
  KEY `VehicleExperienceID_idx` (`VehicleExperienceID`),
  KEY `VehicleCostID_idx` (`VehicleCostID`),
  KEY `VehicleCostGoldID_idx` (`VehicleCostGoldID`),
  CONSTRAINT `VehicleCostGoldID` FOREIGN KEY (`VehicleCostGoldID`) REFERENCES `VehicleCost` (`VehicleCostID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleCostID` FOREIGN KEY (`VehicleCostID`) REFERENCES `VehicleCost` (`VehicleCostID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleCountryID` FOREIGN KEY (`VehicleCountryID`) REFERENCES `Country` (`CountryID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleExperienceID` FOREIGN KEY (`VehicleExperienceID`) REFERENCES `VehicleExperienceRequirement` (`VehicleExperienceID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleTierID` FOREIGN KEY (`VehicleTierID`) REFERENCES `Tier` (`TierID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleTypeID` FOREIGN KEY (`VehicleTypeID`) REFERENCES `VehicleType` (`VehicleTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `OperatorCountryID` FOREIGN KEY (`OperatorCountryID`) REFERENCES `Country` (`CountryID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleTagCorrelations` (
  `VehicleID` int(32) NOT NULL,
  `VehicleTagID` smallint(8) NOT NULL,
  PRIMARY KEY (`VehicleID`,`VehicleTagID`),
  KEY `VehicleTagIDFK_idx` (`VehicleTagID`),
  CONSTRAINT `VehicleTagIDFK` FOREIGN KEY (`VehicleTagID`) REFERENCES `VehicleTags` (`VehicleTagID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleIDFK` FOREIGN KEY (`VehicleID`) REFERENCES `VehicleInformation` (`VehicleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleNames` (
  `VehicleID` int(32) NOT NULL,
  `LanguageID` tinyint(4) NOT NULL,
  `ShopName` varchar(128) DEFAULT NULL,
  `FullName` varchar(128) DEFAULT NULL,
  `ShortName` varchar(128) DEFAULT NULL,
  `CompressedName` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`VehicleID`,`LanguageID`),
  KEY `LanguageIDVehicleNames_idx` (`LanguageID`),
  CONSTRAINT `LanguageIDVehicleNames` FOREIGN KEY (`LanguageID`) REFERENCES `Languages` (`LanguageID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleIDVehicleNames` FOREIGN KEY (`VehicleID`) REFERENCES `VehicleInformation` (`VehicleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Gamemode` (
  `GamemodeID` tinyint(4) NOT NULL AUTO_INCREMENT,
  `GamemodeName` varchar(128) DEFAULT NULL,
  `GamemodeNameHumanReadable` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`GamemodeID`),
  UNIQUE KEY `GamemodeName_UNIQUE` (`GamemodeName`),
  UNIQUE KEY `GamemodeNameHumanReadable_UNIQUE` (`GamemodeNameHumanReadable`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `BattleratingCorrelations` (
  `VehicleID` int(32) NOT NULL,
  `GamemodeID` tinyint(4) NOT NULL,
  `BatleratingID` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`VehicleID`,`GamemodeID`),
  KEY `GamemodeIDBattleratingCorrelation_idx` (`GamemodeID`),
  KEY `BattleratingIDBattleratingCorrelations_idx` (`BatleratingID`),
  CONSTRAINT `BattleratingIDBattleratingCorrelations` FOREIGN KEY (`BatleratingID`) REFERENCES `Battlerating` (`BatleratingID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `GamemodeIDBattleratingCorrelation` FOREIGN KEY (`GamemodeID`) REFERENCES `Gamemode` (`GamemodeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleIDBattleratingCorrelation` FOREIGN KEY (`VehicleID`) REFERENCES `VehicleInformation` (`VehicleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `ModificationStatus` (
  `ModificationStatusID` tinyint(4) NOT NULL,
  `ModificicationStatusText` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`ModificationStatusID`),
  UNIQUE KEY `ModificicationStatusText_UNIQUE` (`ModificicationStatusText`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `GameType` (
  `GameTypeID` tinyint(4) NOT NULL AUTO_INCREMENT,
  `GameTypeName` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`GameTypeID`),
  UNIQUE KEY `GameTypeName_UNIQUE` (`GameTypeName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Titles` (
  `TitleID` int(8) NOT NULL AUTO_INCREMENT,
  `TitleName` varchar(128) NOT NULL,
  `TitleNameHumanReadable` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`TitleID`),
  UNIQUE KEY `TitleName_UNIQUE` (`TitleName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Clans` (
  `ClanID` bigint(16) NOT NULL,
  `ClanName` varchar(128) NOT NULL,
  `ClanTag` varchar(32) NOT NULL,
  `ClanType` tinyint(4) NOT NULL,
  PRIMARY KEY (`ClanID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `ClanRoles` (
  `ClanMemberRoleID` tinyint(4) NOT NULL,
  `ClanMemberRoleName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ClanMemberRoleID`),
  UNIQUE KEY `ClanMemberRoleName_UNIQUE` (`ClanMemberRoleName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Icons` (
  `IconID` int(8) NOT NULL,
  `IconName` varchar(128) NOT NULL,
  PRIMARY KEY (`IconID`),
  UNIQUE KEY `IconName_UNIQUE` (`IconName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `Users` (
  `UserID` bigint(32) NOT NULL,
  `ClanID` bigint(16) DEFAULT NULL,
  `Nickname` varchar(128) DEFAULT NULL,
  `ClanMemberRoleID` tinyint(4) DEFAULT NULL,
  `LastDay` datetime DEFAULT NULL,
  `RegisterDay` datetime DEFAULT NULL,
  `SelectedTitleID` int(8) DEFAULT NULL,
  `IconID` int(8) DEFAULT NULL,
  `PenaltyStatus` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  KEY `ClanIDFK_idx` (`ClanID`),
  KEY `IconIDFK_idx` (`IconID`),
  KEY `SelectedTitleIDFK_idx` (`SelectedTitleID`),
  KEY `ClanMemberRoleID_idx` (`ClanMemberRoleID`),
  CONSTRAINT `ClanIDFK` FOREIGN KEY (`ClanID`) REFERENCES `Clans` (`ClanID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `ClanMemberRoleID` FOREIGN KEY (`ClanMemberRoleID`) REFERENCES `ClanRoles` (`ClanMemberRoleID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `IconIDFK` FOREIGN KEY (`IconID`) REFERENCES `Icons` (`IconID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `SelectedTitleIDFK` FOREIGN KEY (`SelectedTitleID`) REFERENCES `Titles` (`TitleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `TitleCorrelations` (
  `UserID` bigint(32) NOT NULL,
  `TitleID` int(8) NOT NULL,
  PRIMARY KEY (`UserID`,`TitleID`),
  KEY `TitleIDFK_idx` (`TitleID`),
  CONSTRAINT `TitleIDFK` FOREIGN KEY (`TitleID`) REFERENCES `Titles` (`TitleID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `UserIDFK` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `GeneralStats` (
  `Timestamp` datetime NOT NULL,
  `UserID` bigint(32) NOT NULL,
  `Experience` bigint(32) DEFAULT NULL,
  `ExperienceConverted` bigint(32) DEFAULT NULL,
  `NumberOfEliteUnits` int(8) DEFAULT NULL,
  PRIMARY KEY (`Timestamp`,`UserID`),
  KEY `UserIDFK_idx` (`UserID`),
  CONSTRAINT `UserIDGeneralStatsFK` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `VehicleStats` (
  `Timestamp` datetime NOT NULL,
  `UserID` bigint(32) NOT NULL,
  `VehicleID` int(8) NOT NULL,
  `GamemodeID` tinyint(4) NOT NULL,
  `Spawns` int(32) DEFAULT NULL,
  `Deaths` int(32) DEFAULT NULL,
  `ExperienceEarned` bigint(32) DEFAULT NULL,
  `SilverLionsEarned` bigint(32) DEFAULT NULL,
  `GroundKills` int(32) DEFAULT NULL,
  `AirKills` int(32) DEFAULT NULL,
  `NavalKills` int(32) DEFAULT NULL,
  `WasInLineup` int(32) DEFAULT NULL,
  `Defeats` int(32) DEFAULT NULL,
  `Victories` int(32) DEFAULT NULL,
  PRIMARY KEY (`Timestamp`,`UserID`,`VehicleID`,`GamemodeID`),
  KEY `VehicleID_idx` (`VehicleID`),
  KEY `GamemodeIDVehicle_idx` (`GamemodeID`),
  CONSTRAINT `GamemodeIDVehicle` FOREIGN KEY (`GamemodeID`) REFERENCES `Gamemode` (`GamemodeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `TimestampVehicle` FOREIGN KEY (`Timestamp`) REFERENCES `GeneralStats` (`Timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleID` FOREIGN KEY (`VehicleID`) REFERENCES `VehicleInformation` (`VehicleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `ModificationStatusPerUser` (
  `Timestamp` datetime NOT NULL,
  `UserID` bigint(32) NOT NULL,
  `VehicleID` int(8) NOT NULL,
  `ModificationStatusID` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`Timestamp`,`UserID`,`VehicleID`),
  KEY `ModificationStatusPerUserUserID_idx` (`UserID`),
  KEY `ModificationStatusPerUserVehicleID_idx` (`VehicleID`),
  KEY `ModificationStatusPerUserModificationStatus_idx` (`ModificationStatusID`),
  CONSTRAINT `ModificationStatusPerUserModificationStatus` FOREIGN KEY (`ModificationStatusID`) REFERENCES `ModificationStatus` (`ModificationStatusID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `ModificationStatusPerUserTimestamp` FOREIGN KEY (`Timestamp`) REFERENCES `GeneralStats` (`Timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `ModificationStatusPerUserUserID` FOREIGN KEY (`UserID`) REFERENCES `GeneralStats` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `ModificationStatusPerUserVehicleID` FOREIGN KEY (`VehicleID`) REFERENCES `VehicleInformation` (`VehicleID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `SummaryStatsGames` (
  `Timestamp` datetime NOT NULL,
  `UserID` bigint(32) NOT NULL,
  `GameTypeID` tinyint(4) NOT NULL,
  `GamemodeID` tinyint(4) NOT NULL,
  `MissionsCompleted` int(32) DEFAULT NULL,
  `Victories` int(32) DEFAULT NULL,
  PRIMARY KEY (`Timestamp`,`UserID`,`GameTypeID`,`GamemodeID`),
  KEY `SummaryStatsGamesUserID_idx` (`UserID`),
  KEY `SummaryStatsGamesGameTypeID_idx` (`GameTypeID`),
  KEY `SummaryStatsGamesGamemodeID_idx` (`GamemodeID`),
  CONSTRAINT `SummaryStatsGamesGameTypeID` FOREIGN KEY (`GameTypeID`) REFERENCES `GameType` (`GameTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `SummaryStatsGamesGamemodeID` FOREIGN KEY (`GamemodeID`) REFERENCES `Gamemode` (`GamemodeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `SummaryStatsGamesTimestamp` FOREIGN KEY (`Timestamp`) REFERENCES `GeneralStats` (`Timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `SummaryStatsGamesUserID` FOREIGN KEY (`UserID`) REFERENCES `GeneralStats` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE `SummaryStats` (
  `Timestamp` datetime NOT NULL,
  `UserID` bigint(32) NOT NULL,
  `GameTypeID` tinyint(4) NOT NULL,
  `GamemodeID` tinyint(4) NOT NULL,
  `VehicleClassID` tinyint(4) NOT NULL,
  `TimePlayed` bigint(32) DEFAULT NULL,
  `AirKills` int(32) DEFAULT NULL,
  `GroundKills` int(32) DEFAULT NULL,
  `NavalKills` int(32) DEFAULT NULL,
  `Spawns` int(32) DEFAULT NULL,
  `AirKillsAI` int(32) DEFAULT NULL,
  `GroundKillsAI` int(32) DEFAULT NULL,
  `NavalKillsAI` int(32) DEFAULT NULL,
  `AirKillsBot` int(32) DEFAULT NULL,
  `GroundKillsBot` int(32) DEFAULT NULL,
  `NavalKillsBot` int(32) DEFAULT NULL,
  PRIMARY KEY (`Timestamp`,`UserID`,`GameTypeID`,`GamemodeID`,`VehicleClassID`),
  KEY `UserIDSummary_idx` (`UserID`),
  KEY `GameTypeIDSummary_idx` (`GameTypeID`),
  KEY `GamemodeIDSummary_idx` (`GamemodeID`),
  KEY `VehicleClassIDSummary_idx` (`VehicleClassID`),
  CONSTRAINT `GameTypeIDSummary` FOREIGN KEY (`GameTypeID`) REFERENCES `GameType` (`GameTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `GamemodeIDSummary` FOREIGN KEY (`GamemodeID`) REFERENCES `Gamemode` (`GamemodeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `TimestampSummary` FOREIGN KEY (`Timestamp`) REFERENCES `GeneralStats` (`Timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `UserIDSummary` FOREIGN KEY (`UserID`) REFERENCES `GeneralStats` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `VehicleClassIDSummary` FOREIGN KEY (`VehicleClassID`) REFERENCES `VehicleClass` (`VehicleClassID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

INSERT INTO `WarThunderStats`.`Titles` (`TitleName`) VALUES ("");

INSERT INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`,`ClanMemberRoleName`) VALUES (1,'Commander');
INSERT INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`,`ClanMemberRoleName`) VALUES (2,'Officer');
INSERT INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`,`ClanMemberRoleName`) VALUES (3,'Private');
INSERT INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`,`ClanMemberRoleName`) VALUES (5,'Deputy');
INSERT INTO `WarThunderStats`.`ClanRoles` (`ClanMemberRoleID`,`ClanMemberRoleName`) VALUES (6,'Sergeant');

INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_britain','Britain');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_germany','Germany');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_japan','Japan');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_ussr','USSR');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_usa','USA');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_italy','Italy');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_france','France');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_china','China');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_sweden','Sweden');
INSERT INTO `WarThunderStats`.`Country` (`NationName`,`NationNameHumanReadable`) VALUES ('country_israel','Israel');

INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (0,1.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (1,1.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (2,1.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (3,2.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (4,2.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (5,2.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (6,3.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (7,3.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (8,3.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (9,4.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (10,4.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (11,4.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (12,5.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (13,5.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (14,5.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (15,6.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (16,6.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (17,6.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (18,7.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (19,7.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (20,7.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (21,8.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (22,8.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (23,8.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (24,9.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (25,9.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (26,9.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (27,10.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (28,10.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (29,10.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (30,11.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (31,11.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (32,11.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (33,12.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (34,12.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (35,12.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (36,13.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (37,13.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (38,13.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (39,14.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (40,14.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (41,14.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (42,15.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (43,15.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (44,15.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (45,16.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (46,16.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (47,16.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (48,17.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (49,17.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (50,17.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (51,18.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (52,18.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (53,18.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (54,19.0);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (55,19.3);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (56,19.7);
INSERT INTO `WarThunderStats`.`Battlerating` (`BatleratingID`,`BattleratingValue`) VALUES (57,20.0);

INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (1,'I');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (2,'II');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (3,'III');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (4,'IV');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (5,'V');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (6,'VI');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (7,'VII');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (8,'VIII');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (9,'IX');
INSERT INTO `WarThunderStats`.`Tier` (`TierID`,`TierRoman`) VALUES (10,'X');

INSERT INTO `WarThunderStats`.`ModificationStatus` (`ModificationStatusID`,`ModificicationStatusText`) VALUES (0,'0-49% researched');
INSERT INTO `WarThunderStats`.`ModificationStatus` (`ModificationStatusID`,`ModificicationStatusText`) VALUES (1,'50-99% researched');
INSERT INTO `WarThunderStats`.`ModificationStatus` (`ModificationStatusID`,`ModificicationStatusText`) VALUES (2,'Spaded');

UPDATE `WarThunder`.`UpdateQueue` SET `Status` = 0, LastRefresh = DATE_SUB(now(), INTERVAL 7 DAY) WHERE 1=1; 