-- ============================================================
-- EduLink Database Migration Script
-- Run once in phpMyAdmin → SQL tab
-- Safe to run: uses IF NOT EXISTS / IGNORE for idempotency
-- ============================================================

-- --------------------------------------------------------
-- 1. ADD NEW COLUMNS TO users TABLE
-- --------------------------------------------------------

-- Profession tag
ALTER TABLE `users`
  ADD COLUMN IF NOT EXISTS `profession`      ENUM('Student','Teacher','Individual','Professional','Other') NOT NULL DEFAULT 'Student' AFTER `bio`,
  ADD COLUMN IF NOT EXISTS `stacks`          INT(11) NOT NULL DEFAULT 0 AFTER `profession`,
  ADD COLUMN IF NOT EXISTS `streak`          INT(11) NOT NULL DEFAULT 0 AFTER `stacks`,
  ADD COLUMN IF NOT EXISTS `last_login_date` DATE DEFAULT NULL AFTER `streak`,
  ADD COLUMN IF NOT EXISTS `email_notif`     TINYINT(1) NOT NULL DEFAULT 1 AFTER `last_login_date`,
  ADD COLUMN IF NOT EXISTS `whatsapp_notif`  TINYINT(1) NOT NULL DEFAULT 0 AFTER `email_notif`,
  ADD COLUMN IF NOT EXISTS `notif_channel`   ENUM('email','whatsapp','both','none') NOT NULL DEFAULT 'email' AFTER `whatsapp_notif`,
  ADD COLUMN IF NOT EXISTS `privacy`         ENUM('public','friends','private') NOT NULL DEFAULT 'public' AFTER `notif_channel`,
  ADD COLUMN IF NOT EXISTS `show_activity`   TINYINT(1) NOT NULL DEFAULT 1 AFTER `privacy`,
  ADD COLUMN IF NOT EXISTS `avatar_id`       INT(11) NOT NULL DEFAULT 1 AFTER `show_activity`;

-- --------------------------------------------------------
-- 2. INITIALIZE stacks FROM EXISTING focus DATA
-- --------------------------------------------------------
UPDATE `users` u
SET u.`stacks` = COALESCE(
    (SELECT SUM(f.`stacks_earned`) FROM `focus` f WHERE f.`user_id` = u.`user_id`),
    0
)
WHERE u.`stacks` = 0;

-- --------------------------------------------------------
-- 3. ADD room_notes COLUMN TO classroom TABLE
-- --------------------------------------------------------
ALTER TABLE `classroom`
  ADD COLUMN IF NOT EXISTS `room_notes` MEDIUMTEXT DEFAULT NULL AFTER `subject`;

-- --------------------------------------------------------
-- 4. CREATE uploaded_files TABLE
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `uploaded_files` (
  `file_id`          INT(11) NOT NULL AUTO_INCREMENT,
  `user_id`          INT(11) NOT NULL,
  `file_name`        VARCHAR(255) NOT NULL,
  `file_original`    VARCHAR(255) NOT NULL,
  `file_type`        VARCHAR(20)  NOT NULL,
  `file_path`        VARCHAR(500) NOT NULL,
  `file_size`        INT(11) NOT NULL DEFAULT 0,
  `shared`           TINYINT(1)   NOT NULL DEFAULT 0,
  `shared_with`      TEXT DEFAULT NULL,
  `uploaded_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- 5. CREATE stack_history TABLE (audit log)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `stack_history` (
  `id`            INT(11) NOT NULL AUTO_INCREMENT,
  `user_id`       INT(11) NOT NULL,
  `reason`        VARCHAR(100) NOT NULL,
  `stacks_given`  INT(11) NOT NULL DEFAULT 1,
  `awarded_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- 6. CREATE activity_log TABLE (for recent activity on profile)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `activity_log` (
  `log_id`        INT(11) NOT NULL AUTO_INCREMENT,
  `user_id`       INT(11) NOT NULL,
  `action_type`   VARCHAR(50) NOT NULL,
  `action_desc`   VARCHAR(255) NOT NULL,
  `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- 7. UPDATE EXISTING SAMPLE USERS WITH PROFESSION DATA
-- --------------------------------------------------------
UPDATE `users` SET `profession`='Student'      WHERE `user_id` IN (1,2,3,4,5,7,8,9);
UPDATE `users` SET `profession`='Teacher'      WHERE `user_id` = 6;
UPDATE `users` SET `profession`='Professional' WHERE `user_id` = 10;

-- --------------------------------------------------------
-- 8. SEED STACK HISTORY FOR EXISTING USERS
-- --------------------------------------------------------
INSERT IGNORE INTO `stack_history` (`user_id`, `reason`, `stacks_given`) VALUES
(1, 'Initial stacks migration', (SELECT stacks FROM users WHERE user_id = 1)),
(2, 'Initial stacks migration', (SELECT stacks FROM users WHERE user_id = 2));

-- --------------------------------------------------------
-- 9. ADD category + tags TO notes TABLE (for Notebook)
-- --------------------------------------------------------
ALTER TABLE `notes`
  ADD COLUMN IF NOT EXISTS `category` VARCHAR(50) NOT NULL DEFAULT 'general' AFTER `user_id`,
  ADD COLUMN IF NOT EXISTS `tags`     VARCHAR(255) DEFAULT NULL AFTER `category`;

-- --------------------------------------------------------
-- 10. ADD completed_date TO tasks TABLE (for task completion)
-- --------------------------------------------------------
ALTER TABLE `tasks`
  ADD COLUMN IF NOT EXISTS `completed_date` DATE DEFAULT NULL AFTER `status`;

-- --------------------------------------------------------
-- 11. CREATE follows TABLE if not exists
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `follows` (
  `follow_id`    INT(11) NOT NULL AUTO_INCREMENT,
  `follower_id`  INT(11) NOT NULL,
  `following_id` INT(11) NOT NULL,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`follow_id`),
  UNIQUE KEY `unique_follow` (`follower_id`, `following_id`),
  INDEX `idx_following` (`following_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Done!
SELECT 'Migration complete! All tables updated.' AS Status;

