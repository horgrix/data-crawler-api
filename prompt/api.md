# 提供 Steam相关数据 查询API
描述了查询Steam相关数据的可用API接口, 路由以/steam为前缀

# 代码路径
src/data_crawler_api/api/steam_api.py

# 举例
## apiname
### 接收参数
参数名称1 类型 不能为空 描述
参数名称2 类型 可以为空 描述
### 处理逻辑
怎么处理参数
怎么获取数据
如何处理数据
### 返回数据说明
[{
    stat_date：20260615，
    cnt:1000
}]

## query_region_rank
### 接收参数
start_date str 不能为空 格式为yyyymmdd
end_date str 不能为空 格式为yyyymmdd
steam_id int 不能为空 
type str 不能为空 weekly|hourly
### 处理逻辑
数据来源：远程MySQL表
如果 type == hourly，从xd_game_steam_rt_hotlist表查询数据
CREATE TABLE `xd_game_steam_rt_hotlist` (
  `stat_ts` bigint NOT NULL COMMENT '统计时间',
  `rank` int NOT NULL COMMENT '排名',
  `steam_id` int NOT NULL COMMENT 'SteamID',
  `region` varchar(50) NOT NULL COMMENT '区域',
  PRIMARY KEY (`steam_id`, `region`, `stat_ts`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci


如果 type == weekly，从xd_game_steam_weekly_hot_list表查询数据
CREATE TABLE `xd_game_steam_weekly_hot_list` (
  `start_ts` bigint NOT NULL COMMENT '开始时间',
  `end_ts` bigint NOT NULL COMMENT '结束时间',
  `rank` int NOT NULL COMMENT '排名',
  `steam_id` int NOT NULL COMMENT 'SteamID',
  `region` varchar(50) NOT NULL COMMENT '区域',
  PRIMARY KEY (`steam_id`, `region`, `start_ts`, `end_ts`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci

start_ts是时间戳，首先要将start_date，end_date转换为utc时区的时间戳，然后筛选出start_ts在start_date和end_date之间的数据(包含)，查询到的数据，start_ts按utc+8的时区转换成北京时间字符串，格式为yyyymmdd, 并以stat_date返回，其他数据原样返回
### 返回数据说明
[
    {
        stat_date: "20260101",
        steam_id: 123454,
        rank: 1,
        region: "CN"
    }
]

## query_players
### 接收参数
start_date str 不能为空 格式为yyyymmdd
end_date str 不能为空 格式为yyyymmdd
steam_id int 不能为空 
type str 不能为空 monthly|daily|hourly
### 处理逻辑
数据来源：远程MySQL表
CREATE TABLE `xd_game_steam_players` (
  `stat_ts` bigint NOT NULL COMMENT '统计时间',
  `type` varchar(20) NOT NULL COMMENT '时间类型',
  `peak_players` int NOT NULL COMMENT '峰值玩家',
  `steam_id` int NOT NULL COMMENT 'SteamID',
  PRIMARY KEY (`steam_id`, `type`, `stat_ts`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
start_ts是时间戳，首先要将start_date，end_date转换为utc时区的时间戳，然后筛选出start_ts在start_date和end_date之间的数据(包含)，查询到的数据，start_ts按utc+8的时区转换成北京时间字符串，格式为yyyymmdd, 并以stat_date返回，其他数据原样返回
### 返回数据说明
[
    {
        stat_date: "20260101",
        steam_id: 123454,
        peak_players: 1423435
    }
]

## query_recommendations
### 接收参数
start_date str 不能为空 格式为yyyymmdd
end_date str 不能为空 格式为yyyymmdd
steam_id int 不能为空 
type str 不能为空 rollup|recent
### 处理逻辑
数据来源：远程MySQL表
CREATE TABLE `xd_game_steam_commendations` (
  `stat_ts` bigint NOT NULL COMMENT '统计时间',
  `steam_id` int NOT NULL COMMENT 'SteamID',
  `type` varchar(10) NOT NULL COMMENT '类型 recent|rollup',
  `up` int NOT NULL COMMENT '推荐',
  `down` int NOT NULL COMMENT '不推荐',
  `all` int NOT NULL COMMENT '评价数',
  PRIMARY KEY (`steam_id`, `type`, `stat_ts`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
start_ts是时间戳，首先要将start_date，end_date转换为utc时区的时间戳，然后筛选出start_ts在start_date和end_date之间的数据(包含)，查询到的数据，start_ts按utc+8的时区转换成北京时间字符串，格式为yyyymmdd, 并以stat_date返回; 计算推荐率：up/all 保留2位小数，以recommendation_rate字段返回，其他数据原样返回
### 返回数据说明
[
    {
        stat_date: "20260101",
        type: "rollup",
        steam_id: 123454,
        up: 100,
        down: 50,
        all: 150,
        recommendation_rate: 0.66
    }
]

## query_region_code_name_mapping
### 接收参数
不需要接收参数
### 处理逻辑
数据来源：远程MySQL表
CREATE TABLE `steam_region_kv` (
  `code` varchar(8) NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`code`, `name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
查询所有数据，数据原样返回
### 返回数据说明
[
    {
        code: "CN",
        name: "中国"
    }
]