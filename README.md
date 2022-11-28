### 卫健委疫情数据爬取脚本

#### 使用方法
+ 1.爬取最新数据,即今天发布的昨日疫情数据,运行一下命令:
``` 
    python main_script.py --run_type = 0
```

+ 爬取指定某一天的疫情数据,运行一下命令:
```
    python main_script.py --run_type=1 --specify_day=2022-11-26 #例如你想获取26日的疫情数据
```

+ 爬取只从某一时间段的疫情数据,运行一下命令:
```
    python main_script.py --run_type=2 --left_datetime=2022-11-23 --right_datetime=2022-11-26 #例如你想获取23~26号的疫情数据
```

+ 默认的配置文件是 conf/epidemic_wjw.ini,你可以根据需要修改参数,然后指定 --conf_path=xx来生效