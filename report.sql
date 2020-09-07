/*
Navicat MySQL Data Transfer

Source Server         : 159
Source Server Version : 50728
Source Host           : 192.168.1.159:3306
Source Database       : report

Target Server Type    : MYSQL
Target Server Version : 50728
File Encoding         : 65001

Date: 2020-06-02 16:21:23
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for summer_data
-- ----------------------------
DROP TABLE IF EXISTS `summer_data`;
CREATE TABLE `summer_data` (
  `time_t` date NOT NULL,
  `resolved` int(255) DEFAULT NULL,
  `new` int(11) DEFAULT NULL,
  `unresolved` int(11) DEFAULT NULL,
  PRIMARY KEY (`time_t`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
