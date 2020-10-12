

DROP TABLE IF EXISTS `zbx_history_statis`;
CREATE TABLE `zbx_history_statis` (
  `host` varchar(150) NOT NULL COMMENT 'host',
  `item_name` varchar(150) DEFAULT '' COMMENT 'item_name',
  `clock` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `avg_value` double(12,2) NOT NULL DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='zbx历史数据统计表';