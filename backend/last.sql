/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80300 (8.3.0)
 Source Host           : localhost:3306
 Source Schema         : wb_E340

 Target Server Type    : MySQL
 Target Server Version : 80300 (8.3.0)
 File Encoding         : 65001

 Date: 27/05/2024 21:14:37
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin_user
-- ----------------------------
DROP TABLE IF EXISTS `admin_user`;
CREATE TABLE `admin_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `facultyid` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `password` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `jwt_token` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `facultyid` (`facultyid`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of admin_user
-- ----------------------------
BEGIN;
INSERT INTO `admin_user` (`id`, `facultyid`, `name`, `password`, `jwt_token`) VALUES (6, '1160523587', '张三', 'test', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOjE3MTY3ODkzMDAsImlkIjo2fQ.dJmbhxy7ZeEsqwc0ppD5QO5IRfEeiF2_unOz7yEhoIM');
COMMIT;

-- ----------------------------
-- Table structure for devices
-- ----------------------------
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
  `device_id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of devices
-- ----------------------------
BEGIN;
INSERT INTO `devices` (`device_id`, `description`) VALUES (3, '蚂蚁楼3层');
INSERT INTO `devices` (`device_id`, `description`) VALUES (4, '阿里云-1层');
COMMIT;

-- ----------------------------
-- Table structure for disposal_type
-- ----------------------------
DROP TABLE IF EXISTS `disposal_type`;
CREATE TABLE `disposal_type` (
  `device_id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of disposal_type
-- ----------------------------
BEGIN;
INSERT INTO `disposal_type` (`device_id`, `description`) VALUES (1, '有害垃圾');
INSERT INTO `disposal_type` (`device_id`, `description`) VALUES (2, '其他垃圾');
INSERT INTO `disposal_type` (`device_id`, `description`) VALUES (3, '可回收垃圾');
INSERT INTO `disposal_type` (`device_id`, `description`) VALUES (4, '不可回收垃圾');
COMMIT;

-- ----------------------------
-- Table structure for education_info
-- ----------------------------
DROP TABLE IF EXISTS `education_info`;
CREATE TABLE `education_info` (
  `educationid` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` text COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of education_info
-- ----------------------------
BEGIN;
INSERT INTO `education_info` (`educationid`, `name`) VALUES ('14140158', '刘海熠');
COMMIT;

-- ----------------------------
-- Table structure for faculty_info
-- ----------------------------
DROP TABLE IF EXISTS `faculty_info`;
CREATE TABLE `faculty_info` (
  `facultyid` varchar(1024) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` text COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of faculty_info
-- ----------------------------
BEGIN;
INSERT INTO `faculty_info` (`facultyid`, `name`) VALUES ('1160523587', '张三');
INSERT INTO `faculty_info` (`facultyid`, `name`) VALUES ('1160683429', '李四');
INSERT INTO `faculty_info` (`facultyid`, `name`) VALUES ('1160742345', '王五');
COMMIT;

-- ----------------------------
-- Table structure for user_disposal_records
-- ----------------------------
DROP TABLE IF EXISTS `user_disposal_records`;
CREATE TABLE `user_disposal_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_uuid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `image_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `device_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `waste_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `point_status` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of user_disposal_records
-- ----------------------------
BEGIN;
INSERT INTO `user_disposal_records` (`id`, `user_uuid`, `image_path`, `device_id`, `waste_type`, `point_status`, `created_at`) VALUES (1, '935d4d1c-6d94-416e-b22a-bd34e767ee73', '/Users/liuhaiyi/Code/wb/wb_E340/backend/uploads/923c8cb2-c477-447a-831d-6473657941c5.jpg', '1', '1', 'true', '2024-05-25 22:59:20');
INSERT INTO `user_disposal_records` (`id`, `user_uuid`, `image_path`, `device_id`, `waste_type`, `point_status`, `created_at`) VALUES (2, '935d4d1c-6d94-416e-b22a-bd34e767ee73', '/Users/liuhaiyi/Code/wb/wb_E340/backend/uploads/be42c179-3573-4339-92e3-0929335b9158.jpg', '1', '1', 'true', '2024-05-25 23:00:00');
INSERT INTO `user_disposal_records` (`id`, `user_uuid`, `image_path`, `device_id`, `waste_type`, `point_status`, `created_at`) VALUES (3, '935d4d1c-6d94-416e-b22a-bd34e767ee73', '/Users/liuhaiyi/Code/wb/wb_E340/backend/uploads/ec2d2757-9cc4-48e0-b7ac-6f50d5d0df3a.jpg', '2', '3', NULL, '2024-05-26 00:37:47');
INSERT INTO `user_disposal_records` (`id`, `user_uuid`, `image_path`, `device_id`, `waste_type`, `point_status`, `created_at`) VALUES (4, '935d4d1c-6d94-416e-b22a-bd34e767ee73', '/Users/liuhaiyi/Code/wb/wb_E340/backend/uploads/10908fab-11ca-4fd6-ada0-f4ac02243881.jpg', '4', '4', 'true', '2024-05-26 10:41:14');
COMMIT;

-- ----------------------------
-- Table structure for user_info
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) COLLATE utf8mb4_general_ci NOT NULL,
  `educationid` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `jwt_token` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `points` int NOT NULL,
  `college` text COLLATE utf8mb4_general_ci,
  `grade` text COLLATE utf8mb4_general_ci,
  `class` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of user_info
-- ----------------------------
BEGIN;
INSERT INTO `user_info` (`id`, `uuid`, `educationid`, `name`, `password`, `jwt_token`, `points`, `college`, `grade`, `class`) VALUES (1, '935d4d1c-6d94-416e-b22a-bd34e767ee73', '14140158', '刘海熠', 'test', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOjE3MTY3MDUzNTgsInV1aWQiOiI5MzVkNGQxYy02ZDk0LTQxNmUtYjIyYS1iZDM0ZTc2N2VlNzMifQ.EGD3oIpi09nK2s3LcuoN-YGMCjAsdXQ8LcsjWe3l0C8', 3, '信息学院', '大3', '4班');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
