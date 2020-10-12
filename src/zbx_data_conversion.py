import os

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, EnvironmentSettings 
from pyflink.table import DataTypes
from util import get_first_item, ts2str, no2ts
from pyflink.table.descriptors import Schema, Kafka, Json
from pyflink.table.window import Tumble


# 创建Table Environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)
# env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

t_env = StreamTableEnvironment.create(env)
   # environment_settings=EnvironmentSettings.new_instance().use_blink_planner().build())


t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)
t_env.register_function("ts2str", ts2str)


t_env.connect(
    Kafka()
        .version("universal")
        .topic("zbxmetric-pre")
        .property("bootstrap.servers", "localhost:9092")
        .property("zookeeper.connect", "localhost:2181")
        .start_from_latest()
    ) \
    .with_format(
    Json()
        .json_schema(
            """
            {
                "type": "object",
                "properties": {
                  "itemid": {
                    "type": "integer"
                  },
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
                    "type": "number"
                  }
                }
            }
            """
        )
    )\
    .with_schema(
        Schema()
        .field("name", DataTypes.STRING())
        .field("value", DataTypes.DECIMAL(11, 2))
        .field("host", DataTypes.STRING())
        .field("clock", DataTypes.DECIMAL(11, 2))
        # .field("applications", DataTypes.ARRAY(DataTypes.STRING()))
    ) \
    .register_table_source("INPUT_TABLE")

t_env.connect(
    Kafka()
    .version("universal")
    .topic("zbxmetric")
    .property("bootstrap.servers", "localhost:9092")
    .property("zookeeper.connect", "localhost:2181")
    .start_from_latest()
) \
    .with_format(
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
               "type": "string"
           }
       }
   }
        """
        )
    ) \
    .with_schema(
        Schema()
        .field("name", DataTypes.STRING())
        .field("value", DataTypes.DECIMAL(11, 2))
        .field("host", DataTypes.STRING())
        .field("clock", DataTypes.STRING())
) \
    .register_table_sink("OUTPUT_TABLE")


t_env.scan("INPUT_TABLE") \
    .filter("name = 'CPU Used'") \
    .filter("name = 'Connection'") \
    .filter("name = '[CPU]Processor Util (1Min Average)'") \
    .filter("name = 'con'") \
    .filter("name = 'TCP_ESTABLISHED'") \
    .select("name, value, host, ts2str(clock) as clock") \
    .insert_into("OUTPUT_TABLE")

    # .filter("name = '[Harddisk] IO Write/s'") \
    # .filter("name = '[Harddisk] IO Read/s'") \
    # .filter("name = 'TCP CLOSE_WAIT'") \
    # .filter("name = 'Outgoing network traffic on eth0'") \
    # .filter("name = 'Incoming network traffic on eth0'") \

t_env.execute("zbx-data-convert")