CREATE TABLE `analyses` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`title` varchar(255) NOT NULL,
	`description` text,
	`status` enum('processing','completed','failed') NOT NULL DEFAULT 'processing',
	`filesAnalyzed` int NOT NULL DEFAULT 0,
	`peopleFound` int NOT NULL DEFAULT 0,
	`relationshipsFound` int NOT NULL DEFAULT 0,
	`processingStartedAt` timestamp NOT NULL DEFAULT (now()),
	`processingCompletedAt` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `analyses_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `analysisReports` (
	`id` int AUTO_INCREMENT NOT NULL,
	`analysisId` int NOT NULL,
	`textReport` text NOT NULL,
	`csvPeopleUrl` varchar(512),
	`csvRelationshipsUrl` varchar(512),
	`networkGraphUrl` varchar(512),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `analysisReports_id` PRIMARY KEY(`id`),
	CONSTRAINT `analysisReports_analysisId_unique` UNIQUE(`analysisId`)
);
--> statement-breakpoint
CREATE TABLE `entities` (
	`id` int AUTO_INCREMENT NOT NULL,
	`analysisId` int NOT NULL,
	`name` varchar(255) NOT NULL,
	`type` enum('person','email','phone') NOT NULL DEFAULT 'person',
	`normalizedName` varchar(255) NOT NULL,
	`fileCount` int NOT NULL DEFAULT 1,
	`connectionCount` int NOT NULL DEFAULT 0,
	`emails` json,
	`phones` json,
	`firstSeenAt` timestamp NOT NULL DEFAULT (now()),
	`lastSeenAt` timestamp NOT NULL DEFAULT (now()),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `entities_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `entityFileAssociations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`entityId` int NOT NULL,
	`fileId` int NOT NULL,
	`occurrenceCount` int NOT NULL DEFAULT 1,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `entityFileAssociations_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `files` (
	`id` int AUTO_INCREMENT NOT NULL,
	`analysisId` int NOT NULL,
	`fileName` varchar(512) NOT NULL,
	`fileType` varchar(50) NOT NULL,
	`fileSize` int NOT NULL,
	`s3Key` varchar(512) NOT NULL,
	`s3Url` text NOT NULL,
	`source` enum('upload','google_drive') NOT NULL DEFAULT 'upload',
	`googleDriveFileId` varchar(255),
	`entitiesExtracted` int NOT NULL DEFAULT 0,
	`processingStatus` enum('pending','processing','completed','failed') NOT NULL DEFAULT 'pending',
	`errorMessage` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `files_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `googleDriveAccounts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`email` varchar(320) NOT NULL,
	`accessToken` text NOT NULL,
	`refreshToken` text,
	`tokenExpiresAt` timestamp,
	`isActive` boolean NOT NULL DEFAULT true,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `googleDriveAccounts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `relationships` (
	`id` int AUTO_INCREMENT NOT NULL,
	`analysisId` int NOT NULL,
	`entity1Id` int NOT NULL,
	`entity2Id` int NOT NULL,
	`coOccurrenceCount` int NOT NULL DEFAULT 1,
	`strength` decimal(5,2) DEFAULT '1.0',
	`firstSeenAt` timestamp NOT NULL DEFAULT (now()),
	`lastSeenAt` timestamp NOT NULL DEFAULT (now()),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `relationships_id` PRIMARY KEY(`id`)
);
