-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 28, 2026 at 08:55 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `edulink`
--

-- --------------------------------------------------------

--
-- Table structure for table `classroom`
--

CREATE TABLE `classroom` (
  `room_id` int(11) NOT NULL,
  `room_name` varchar(30) NOT NULL,
  `room_description` text NOT NULL,
  `admin_id` int(11) NOT NULL,
  `created_date` date NOT NULL,
  `total_duration` varchar(20) NOT NULL DEFAULT '0h',
  `subject` varchar(50) NOT NULL DEFAULT 'General'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `classroom`
--

INSERT INTO `classroom` (`room_id`, `room_name`, `room_description`, `admin_id`, `created_date`, `total_duration`, `subject`) VALUES
(1, 'abc', 'hfhjfub 8i', 1, '2026-03-25', '0h', 'Physics');

-- --------------------------------------------------------

--
-- Table structure for table `classroom_messages`
--

CREATE TABLE `classroom_messages` (
  `msg_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `community`
--

CREATE TABLE `community` (
  `group_id` int(11) NOT NULL,
  `group_name` varchar(30) NOT NULL,
  `group_description` text NOT NULL,
  `admin_id` int(11) NOT NULL,
  `group_member_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `community_messages`
--

CREATE TABLE `community_messages` (
  `msg_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `subject` varchar(30) NOT NULL DEFAULT 'general',
  `message` text NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `focus`
--

CREATE TABLE `focus` (
  `focus_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `task_name` varchar(100) DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `sessions_count` int(11) NOT NULL DEFAULT 0,
  `session_date` datetime DEFAULT current_timestamp(),
  `stacks_earned` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `focus`
--

INSERT INTO `focus` (`focus_id`, `user_id`, `task_name`, `duration_minutes`, `sessions_count`, `session_date`, `stacks_earned`) VALUES
(1, 1, 'Meditation', 1, 1, '2026-02-16 22:49:10', 1);

-- --------------------------------------------------------

--
-- Table structure for table `follows`
--

CREATE TABLE `follows` (
  `follow_id` int(11) NOT NULL,
  `follower_id` int(11) NOT NULL,
  `following_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `follows`
--

INSERT INTO `follows` (`follow_id`, `follower_id`, `following_id`, `created_at`) VALUES
(1, 1, 3, '2026-03-28 13:23:05'),
(2, 1, 5, '2026-03-28 13:23:09'),
(3, 1, 7, '2026-03-28 13:23:12'),
(4, 1, 9, '2026-03-28 13:23:16'),
(5, 1, 10, '2026-03-28 13:23:20'),
(6, 2, 1, '2026-03-28 13:24:19');

-- --------------------------------------------------------

--
-- Table structure for table `group_members`
--

CREATE TABLE `group_members` (
  `id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `join_date` date NOT NULL,
  `admin_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notes`
--

CREATE TABLE `notes` (
  `notes_id` int(11) NOT NULL,
  `notes_title` varchar(100) NOT NULL DEFAULT 'Untitled Note',
  `notes_description` text NOT NULL,
  `created_date` date NOT NULL,
  `user_id` int(11) NOT NULL,
  `category` varchar(30) NOT NULL DEFAULT 'general',
  `tags` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notes`
--

INSERT INTO `notes` (`notes_id`, `notes_title`, `notes_description`, `created_date`, `user_id`, `category`, `tags`) VALUES
(1, 'DBMS Normalization', '1NF, 2NF, 3NF aur BCNF ke rules aur examples', '2026-03-26', 1, 'DBMS', 'normalization,dbms,concept'),
(2, 'Operating System Scheduling', 'FCFS, SJF, Round Robin scheduling algorithms ke notes', '2026-03-26', 2, 'OS', 'cpu scheduling,os'),
(3, 'DSA Arrays', 'Array traversal, insertion, deletion aur problems', '2026-03-27', 1, 'DSA', 'arrays,leetcode'),
(4, 'Flask Basics', 'Routing, templates, request-response cycle in Flask', '2026-03-27', 1, 'Web Dev', 'flask,python'),
(5, 'Machine Learning Intro', 'Supervised vs Unsupervised learning basics', '2026-03-28', 1, 'AI/ML', 'ml,basics'),
(6, 'SQL Joins', 'Inner join, left join, right join ke examples', '2026-03-28', 2, 'DBMS', 'sql,joins'),
(7, 'Java OOP Concepts', 'Encapsulation, Inheritance, Polymorphism, Abstraction', '2026-03-29', 2, 'Programming', 'java,oops'),
(8, 'System Design Basics', 'Scalability, load balancing, caching concepts', '2026-03-30', 1, 'System Design', 'scalability,design'),
(9, 'Aptitude Formulas', 'Profit-loss, time-work, percentage formulas', '2026-03-30', 2, 'Aptitude', 'maths,formulas'),
(11, 'Mock Interview', 'Interview given daily Interview given daily Interview given daily', '2026-03-27', 1, 'general', '');

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `subject` varchar(30) NOT NULL DEFAULT 'general',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `post_comments`
--

CREATE TABLE `post_comments` (
  `comment_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `comment` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `post_likes`
--

CREATE TABLE `post_likes` (
  `like_id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `room_members`
--

CREATE TABLE `room_members` (
  `id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `join_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tasks`
--

CREATE TABLE `tasks` (
  `task_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `task_title` varchar(30) NOT NULL,
  `task_description` text NOT NULL,
  `due_date` date NOT NULL,
  `due_time` time NOT NULL,
  `recurring` varchar(20) NOT NULL DEFAULT 'once',
  `priority` varchar(15) NOT NULL DEFAULT 'medium',
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `created_date` date NOT NULL,
  `completed_date` date NOT NULL DEFAULT '0000-00-00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tasks`
--

INSERT INTO `tasks` (`task_id`, `user_id`, `task_title`, `task_description`, `due_date`, `due_time`, `recurring`, `priority`, `status`, `created_date`, `completed_date`) VALUES
(1, 1, 'DSA Practice', 'Solve 5 problems of arrays from LeetCode', '2026-03-26', '18:00:00', 'daily', 'high', 'completed', '2026-03-26', '2026-03-27'),
(2, 1, 'DBMS Revision', 'Revise normalization and ER diagrams', '2026-03-28', '16:00:00', 'once', 'medium', 'pending', '2026-03-26', '0000-00-00'),
(3, 2, 'Flask Project Work', 'Implement login authentication module', '2026-03-26', '20:00:00', 'once', 'high', 'pending', '2026-03-26', '0000-00-00'),
(4, 2, 'AI/ML Study', 'Watch 2 lectures on supervised learning', '2026-03-27', '15:00:00', 'daily', 'medium', 'pending', '2026-03-26', '0000-00-00'),
(5, 1, 'Aptitude Practice', 'Solve 20 quantitative aptitude questions', '2026-03-26', '10:00:00', 'daily', 'low', 'completed', '2026-03-26', '2026-03-27'),
(6, 1, 'Resume Update', 'Add recent projects and improve summary', '2026-03-30', '12:00:00', 'once', 'high', 'pending', '2026-03-26', '0000-00-00'),
(7, 1, 'System Design Basics', 'Learn about scalability and load balancing', '2026-03-31', '19:00:00', 'once', 'medium', 'pending', '2026-03-26', '0000-00-00'),
(8, 2, 'Coding Contest', 'Participate in weekly coding contest', '2026-03-28', '21:00:00', 'weekly', 'high', 'pending', '2026-03-26', '0000-00-00'),
(9, 1, 'Notes Making', 'Prepare notes for Operating System topics', '2026-03-29', '14:00:00', 'once', 'medium', 'pending', '2026-03-26', '0000-00-00'),
(10, 2, 'Mock Interview', 'Practice HR + technical interview questions', '2026-04-01', '17:00:00', 'once', 'high', 'pending', '2026-03-26', '0000-00-00'),
(11, 1, 'Practice test', 'prepare of exam', '2026-03-26', '22:59:00', 'once', 'medium', 'completed', '2026-03-26', '2026-03-27');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL COMMENT 'User Id',
  `profile_pic` text NOT NULL,
  `background_pic` text NOT NULL,
  `profilename` varchar(50) NOT NULL COMMENT 'Display name',
  `username` varchar(50) NOT NULL,
  `whatsapp` varchar(15) NOT NULL,
  `email` varchar(250) NOT NULL,
  `password` varchar(255) NOT NULL,
  `bio` varchar(300) NOT NULL DEFAULT '',
  `created_date` date NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `profile_pic`, `background_pic`, `profilename`, `username`, `whatsapp`, `email`, `password`, `bio`, `created_date`) VALUES
(1, 'user.jpg', 'cover.jpg', 'Khushi Shewale', 'oceaniccoderx', '7558569152', 'khushishewale797@gmail.com', 'Khushi@123', 'Energetic student', '2026-02-26'),
(2, 'profile2.jpg', 'bg2.jpg', 'Aarav Sharma', 'aarav_01', '9876543210', 'aarav@gmail.com', 'Pass@123', 'Aspiring software developer', '2026-03-25'),
(3, 'profile3.jpg', 'bg3.jpg', 'Sneha Patil', 'sneha_codes', '9123456780', 'sneha@gmail.com', 'Pass@123', 'Frontend developer & UI designer', '2026-03-25'),
(4, 'profile4.jpg', 'bg4.jpg', 'Rohit Verma', 'rohit_dev', '9988776655', 'rohit@gmail.com', 'Pass@123', 'Python & Flask enthusiast', '2026-03-26'),
(5, 'profile5.jpg', 'bg5.jpg', 'Priya Singh', 'priya_ai', '9012345678', 'priya@gmail.com', 'Pass@123', 'AI/ML learner', '2026-03-26'),
(6, 'profile6.jpg', 'bg6.jpg', 'Kunal Mehta', 'kunal_tech', '9090909090', 'kunal@gmail.com', 'Pass@123', 'Full stack developer', '2026-03-27'),
(7, 'profile7.jpg', 'bg7.jpg', 'Neha Joshi', 'neha_study', '9898989898', 'neha@gmail.com', 'Pass@123', 'Preparing for tech interviews', '2026-03-27'),
(8, 'profile8.jpg', 'bg8.jpg', 'Aditya Kulkarni', 'adi_codes', '9765432109', 'aditya@gmail.com', 'Pass@123', 'DSA practice daily', '2026-03-28'),
(9, 'profile9.jpg', 'bg9.jpg', 'Pooja Deshmukh', 'pooja_dev', '9345678901', 'pooja@gmail.com', 'Pass@123', 'Backend developer', '2026-03-28'),
(10, 'profile10.jpg', 'bg10.jpg', 'Rahul Yadav', 'rahul_js', '9234567890', 'rahul@gmail.com', 'Pass@123', 'JavaScript & React lover', '2026-03-29');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `classroom`
--
ALTER TABLE `classroom`
  ADD PRIMARY KEY (`room_id`);

--
-- Indexes for table `classroom_messages`
--
ALTER TABLE `classroom_messages`
  ADD PRIMARY KEY (`msg_id`);

--
-- Indexes for table `community`
--
ALTER TABLE `community`
  ADD PRIMARY KEY (`group_id`);

--
-- Indexes for table `community_messages`
--
ALTER TABLE `community_messages`
  ADD PRIMARY KEY (`msg_id`);

--
-- Indexes for table `focus`
--
ALTER TABLE `focus`
  ADD PRIMARY KEY (`focus_id`);

--
-- Indexes for table `follows`
--
ALTER TABLE `follows`
  ADD PRIMARY KEY (`follow_id`),
  ADD UNIQUE KEY `unique_follow` (`follower_id`,`following_id`);

--
-- Indexes for table `group_members`
--
ALTER TABLE `group_members`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_group_member` (`member_id`,`group_id`);

--
-- Indexes for table `notes`
--
ALTER TABLE `notes`
  ADD PRIMARY KEY (`notes_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_id`);

--
-- Indexes for table `post_comments`
--
ALTER TABLE `post_comments`
  ADD PRIMARY KEY (`comment_id`);

--
-- Indexes for table `post_likes`
--
ALTER TABLE `post_likes`
  ADD PRIMARY KEY (`like_id`),
  ADD UNIQUE KEY `unique_like` (`post_id`,`user_id`);

--
-- Indexes for table `room_members`
--
ALTER TABLE `room_members`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_member_room` (`member_id`,`room_id`);

--
-- Indexes for table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`task_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `classroom`
--
ALTER TABLE `classroom`
  MODIFY `room_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `classroom_messages`
--
ALTER TABLE `classroom_messages`
  MODIFY `msg_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `community`
--
ALTER TABLE `community`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `community_messages`
--
ALTER TABLE `community_messages`
  MODIFY `msg_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `focus`
--
ALTER TABLE `focus`
  MODIFY `focus_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `follows`
--
ALTER TABLE `follows`
  MODIFY `follow_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `group_members`
--
ALTER TABLE `group_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notes`
--
ALTER TABLE `notes`
  MODIFY `notes_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `post_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `post_comments`
--
ALTER TABLE `post_comments`
  MODIFY `comment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `post_likes`
--
ALTER TABLE `post_likes`
  MODIFY `like_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `room_members`
--
ALTER TABLE `room_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tasks`
--
ALTER TABLE `tasks`
  MODIFY `task_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'User Id', AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
