## zabbix数据写入本地文件

### zabbix_server.conf 添加配置项(4.0+版本才支持)

- 编辑zabbix_server.conf添加如下配置项ExportDir、ExportFileSize, 配置项的值根据实际情况调整
```javascript
ExportDir=/data/zabbix/export
ExportFileSize=100M
```

- 添加完配置后重启zabbix server服务, /data/zabbix/export目录将会产生如下文件:
```
-rw-rw-r-- 1 zabbix zabbix 103266751 10月 11 16:25 history-history-syncer-1.ndjson
-rw-rw-r-- 1 zabbix zabbix         0 8月  18 20:00 history-main-process-0.ndjson
-rw-rw-r-- 1 zabbix zabbix   2196999 10月 11 15:44 problems-history-syncer-1.ndjson
-rw-rw-r-- 1 zabbix zabbix         0 8月  18 20:00 problems-main-process-0.ndjson
-rw-rw-r-- 1 zabbix zabbix         0 8月  18 20:00 problems-task-manager-1.ndjson
-rw-rw-r-- 1 zabbix zabbix         0 8月  18 20:00 trends-history-syncer-1.ndjson
-rw-rw-r-- 1 zabbix zabbix         0 8月  18 20:00 trends-main-process-0.ndjson
```


## logstash收集本地数据文件并推入Kafka
kafka及logstash的安装这里不阐述, 本示例logstash安装路径为/usr/local/logstash
这里我们只收集history数据进行演示, 即history-history-syncer开头的文件, 文件内容均为json格式
数据写入topic: zbxmetric-pre, bootstrap_servers为Kafka服务的地址

- 添加配置文件 /usr/local/logstash/conf/zbx_history.conf
```javascript

input {
    file  {
        path => ["/data/zabbix/export/history-history-syncer-*.ndjson"]
        codec => json
    }
}

output {
    kafka {
        codec => json
        topic_id => "zbxmetric-pre"
        bootstrap_servers => "localhost:9092"
    }
    #stdout { codec => rubydebug }
}
```

- 启动logstash
```javascript
/usr/local/logstash/bin/logstash -f /usr/local/logstash/conf/zbx_history.conf
```
- logstash启动后输入如下日子则表示启动成功(想要知道有没有成功收集数据可以在启动命令追加 --debug)
```
[2020-10-11T17:04:56,718][INFO ][logstash.pipeline        ] Starting pipeline {"id"=>"main", "pipeline.workers"=>4, "pipeline.batch.size"=>125, "pipeline.batch.delay"=>5, "pipeline.max_inflight"=>500}
[2020-10-11T17:04:56,882][INFO ][logstash.pipeline        ] Pipeline main started
[2020-10-11T17:04:56,969][INFO ][logstash.agent           ] Successfully started Logstash API endpoint {:port=>9600}
```