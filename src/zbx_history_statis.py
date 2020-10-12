import os

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, EnvironmentSettings 
from pyflink.table import DataTypes, types, Row
from util import get_first_item, p99
from connector_ddl import kafka_zbx_source_ddl, mysql_zbx_history_ddl
from pyflink.table.descriptors import Schema, Kafka, Json, Rowtime
from pyflink.table.window import Tumble


env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

t_env = StreamTableEnvironment.create(env)
   # environment_settings=EnvironmentSettings.new_instance().use_blink_planner().build())


t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)

# 创建Kafka数据源表
# t_env.sql_update(kafka_zbx_source_ddl)

t_env.connect(
  Kafka()
  .version("universal")
  .topic("zbxmetric")
  .property("bootstrap.servers", "localhost:9092")
  .property("zookeeper.connect", "localhost:2181")
  .property("group.id", "flink-zbx_history_statis")
  .start_from_latest()
).with_format(
  Json()
  .json_schema(
    """
      {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "value": {
            "type": "number"
          },
          "host": {
            "type": "string"
          },
          "clock": {
            "type": "string",
            "format": "date-time"
          }
        }
    }
    """
  )
).with_schema(
  Schema()
    .field("name", DataTypes.STRING())
    .field("value", DataTypes.DECIMAL(11, 2))
    .field("host", DataTypes.STRING())
    .field("rowtime", DataTypes.TIMESTAMP(3))
      .rowtime(
        Rowtime()
            .timestamps_from_field("clock")
            .watermarks_periodic_bounded(60000)
      )
).in_append_mode().register_table_source("zbx_history_data")

# 创建MySql结果表
t_env.sql_update(mysql_zbx_history_ddl)

t_env.add_python_file(os.path.dirname(
    os.path.abspath(__file__)) + "/util.py")
t_env.add_python_file(os.path.dirname(
    os.path.abspath(__file__)) + "/connector_ddl.py")

# 核心的统计逻辑
# Tumble.over("1.minutes").on("clock")
t_env.scan("zbx_history_data").window(Tumble.over("5.minutes").on("rowtime").alias("w"))\
   .group_by("w, "
             "host, "
             "name")\
   .select(
           "host, "
           "name as item_name, "
           "w.end as clock, "
           "avg(value) as avg_value") \
   .insert_into("zbx_history_statis")

# 执行作业
t_env.execute("job-zbx_history_statis")
