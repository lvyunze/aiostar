
# 基于sanic以及aiohttp的web爬虫框架

## 特点
✓ 基于sanic以及aiohttp，性能较好

✓ 支持restful以及yield形式调用

✓ 完成爬虫调度器、引擎以及中间件相关封装

✓ 日志封装,并且支持中间件二次开发

✓ 创建爬虫文件简单，直接新建文件即可，同时也可以当做restful api来使用

✓ 支持热加载，结合supervisord部署更佳

## 使用


#### 1、运行run.py文件
``
python3.7 run.py 6060
``
#### 2、在spider下创建爬虫py文件（例如 yz:demo）
#### 3、爬虫调用
```angular2html
http://0.0.0.0:6060/fetch/?&spider=yz.demo
```

## todo

- aiostar命令行工具开发

- 数据库相关封装

- 配置文件封装

## 相关链接

1. https://github.com/sanic-org/sanic
1. https://github.com/scrapy/scrapy
