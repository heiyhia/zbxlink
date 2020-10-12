
kafka_zbx_source_ddl = """
CREATE TABLE zbx_history_data (
 host VARCHAR,
 name VARCHAR,
 clock TIMESTAMP(3),
 `value` DOUBLE
) WITH (
 'connector.type' = 'kafka',
 'connector.version' = 'universal',
 'connector.topic' = 'zbxmetric',
 'connector.properties.zookeeper.connect' = 'localhost:2181',
 'connector.properties.bootstrap.servers' = 'localhost:9092',
 'connector.properties.group.id' = 'flink-zbx_history_statis',
 'format.type' = 'csv',
 'format.ignore-parse-errors' = 'true'
)
"""


mysql_zbx_history_ddl = """
CREATE TABLE zbx_history_statis (
 host VARCHAR,
 item_name VARCHAR,
 clock TIMESTAMP(3),
 avg_value DECIMAL(38, 18)
) WITH (
 'connector.type' = 'jdbc',
 'connector.url' = 'jdbc:mysql://localhost:3306/your_db',
 'connector.table' = 'your_table',
 'connector.username' = 'username',
 'connector.password' = 'password',
 'connector.write.flush.interval' = '1s'
)
"""

