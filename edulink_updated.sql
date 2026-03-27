-- ============================================================
-- EduLink — Updated Database Schema (Flask Version)
-- Changes from original:
--   1. notes: added user_id, category, tags columns
--   2. users: password column size increased to 255
--   3. classroom: added subject column
--   4. room_members: member_id now clearly references users.user_id
--   5. New tables: classroom_messages, posts, post_likes, post_comments,
--                  community_messages, follows, group_members (updated)
-- ============================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- ── Database ─────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS `edulink` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `edulink`;


-- ── users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `users` (
  `user_id`        int(11)      NOT NULL AUTO_INCREMENT COMMENT 'User Id',
  `profile_pic`    text         NOT NULL,
  `background_pic` text         NOT NULL,
  `profilename`    varchar(50)  NOT NULL COMMENT 'Display name',
  `username`       varchar(50)  NOT NULL,
  `whatsapp`       varchar(15)  NOT NULL,
  `email`          varchar(250) NOT NULL,
  `password`       varchar(255) NOT NULL,   -- increased from 10 (bcrypt ready)
  `bio`            varchar(300) NOT NULL DEFAULT '',
  `created_date`   date         NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Sample user (password: Khushi@123)
INSERT IGNORE INTO `users`
  (`user_id`,`profile_pic`,`background_pic`,`profilename`,`username`,`whatsapp`,`email`,`password`,`bio`,`created_date`)
VALUES
  (1,'user.jpg','cover.jpg','Khushi Shewale','oceaniccoderx','7558569152','khushishewale797@gmail.com','Khushi@123','Energetic student','2026-02-26');


-- ── tasks ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `tasks` (
  `task_id`          int(11)     NOT NULL AUTO_INCREMENT,
  `user_id`          int(11)     NOT NULL,
  `task_title`       varchar(30) NOT NULL,
  `task_description` text        NOT NULL,
  `due_date`         date        NOT NULL,
  `due_time`         time        NOT NULL,
  `recurring`        varchar(20) NOT NULL DEFAULT 'once',
  `priority`         varchar(15) NOT NULL DEFAULT 'medium',
  `status`           varchar(20) NOT NULL DEFAULT 'pending',
  `created_date`     date        NOT NULL,
  `completed_date`   date        NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── focus ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `focus` (
  `focus_id`         int(11) NOT NULL AUTO_INCREMENT,
  `user_id`          int(11) NOT NULL,
  `task_name`        varchar(100) DEFAULT NULL,
  `duration_minutes` int(11)      DEFAULT NULL,
  `sessions_count`   int(11)      NOT NULL DEFAULT 0,
  `session_date`     datetime     DEFAULT current_timestamp(),
  `stacks_earned`    int(11)      DEFAULT 1,
  PRIMARY KEY (`focus_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT IGNORE INTO `focus` (`focus_id`,`user_id`,`task_name`,`duration_minutes`,`sessions_count`,`session_date`,`stacks_earned`)
VALUES (1,1,'Meditation',1,1,'2026-02-16 22:49:10',10);


-- ── notes (UPDATED — added user_id, category, tags) ─────────
CREATE TABLE IF NOT EXISTS `notes` (
  `notes_id`          int(11)     NOT NULL AUTO_INCREMENT,
  `notes_title`       varchar(100) NOT NULL DEFAULT 'Untitled Note',
  `notes_description` text         NOT NULL,
  `created_date`      date         NOT NULL,
  `user_id`           int(11)      NOT NULL,    -- NEW: linked to user
  `category`          varchar(30)  NOT NULL DEFAULT 'general',  -- NEW
  `tags`              text                  DEFAULT NULL,       -- NEW
  PRIMARY KEY (`notes_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── classroom (UPDATED — added subject) ─────────────────────
CREATE TABLE IF NOT EXISTS `classroom` (
  `room_id`          int(11)     NOT NULL AUTO_INCREMENT,
  `room_name`        varchar(30) NOT NULL,
  `room_description` text        NOT NULL,
  `admin_id`         int(11)     NOT NULL,
  `created_date`     date        NOT NULL,
  `total_duration`   varchar(20) NOT NULL DEFAULT '0h',
  `subject`          varchar(50) NOT NULL DEFAULT 'General',   -- NEW
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── room_members ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `room_members` (
  `id`        int(11) NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL,   -- this is the user_id of the member
  `room_id`   int(11) NOT NULL,
  `join_date` date    NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_member_room` (`member_id`, `room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── classroom_messages (NEW) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS `classroom_messages` (
  `msg_id`  int(11)      NOT NULL AUTO_INCREMENT,
  `room_id` int(11)      NOT NULL,
  `user_id` int(11)      NOT NULL,
  `message` text         NOT NULL,
  `sent_at` datetime     NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── community (groups) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS `community` (
  `group_id`          int(11)     NOT NULL AUTO_INCREMENT,
  `group_name`        varchar(30) NOT NULL,
  `group_description` text        NOT NULL,
  `admin_id`          int(11)     NOT NULL,
  `group_member_id`   int(11)     NOT NULL,   -- kept for compatibility
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── group_members ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `group_members` (
  `id`        int(11) NOT NULL AUTO_INCREMENT,
  `member_id` int(11) NOT NULL,
  `group_id`  int(11) NOT NULL,
  `join_date` date    NOT NULL,
  `admin_id`  int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_group_member` (`member_id`, `group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── community_messages (NEW) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS `community_messages` (
  `msg_id`  int(11)     NOT NULL AUTO_INCREMENT,
  `group_id` int(11)    NOT NULL,
  `user_id` int(11)     NOT NULL,
  `subject` varchar(30) NOT NULL DEFAULT 'general',
  `message` text        NOT NULL,
  `sent_at` datetime    NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── posts (NEW — community feed) ─────────────────────────────
CREATE TABLE IF NOT EXISTS `posts` (
  `post_id`    int(11) NOT NULL AUTO_INCREMENT,
  `user_id`    int(11) NOT NULL,
  `content`    text    NOT NULL,
  `subject`    varchar(30) NOT NULL DEFAULT 'general',
  `created_at` datetime    NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── post_likes (NEW) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `post_likes` (
  `like_id` int(11) NOT NULL AUTO_INCREMENT,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`like_id`),
  UNIQUE KEY `unique_like` (`post_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── post_comments (NEW) ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS `post_comments` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `post_id`    int(11) NOT NULL,
  `user_id`    int(11) NOT NULL,
  `comment`    text    NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ── follows (NEW — friend/follow system) ─────────────────────
CREATE TABLE IF NOT EXISTS `follows` (
  `follow_id`    int(11) NOT NULL AUTO_INCREMENT,
  `follower_id`  int(11) NOT NULL,   -- jo follow kar raha hai
  `following_id` int(11) NOT NULL,   -- jisko follow kiya
  `created_at`   datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`follow_id`),
  UNIQUE KEY `unique_follow` (`follower_id`, `following_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


COMMIT;
