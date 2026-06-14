# 提供 Steam相关数据 查询API
描述了查询 XD 相关数据的可用API接口, 路由以 /xd 为前缀

# 代码路径
src/data_crawler_api/api/xd_api.py

# 举例
## apiname
api说明
## path
/xxx
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

## query_xd_steam_games
查询心动在Steam的所有游戏
### path
/games
### 接收参数
不需要参数
### 处理逻辑
数据来源：远程MySQL表
CREATE TABLE `xd_game_steamids` (
  `steam_id` bigint NOT NULL,
  `steam_name` varchar(128) NOT NULL,
  PRIMARY KEY (`steam_id`, `steam_name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
返回全部数据，数据缓存在内存里，每1小时失效一次
### 返回数据说明
[
    {
        steam_id: 123454,
        steam_name: "心动小镇"
    }
]

## query_xd_torchlight_season
查询心动的【火炬之光】赛季配置信息
### path
/games/torchlight/season/configs
### 接收参数
不需要参数
### 处理逻辑
CREATE TABLE `xd_torchlight_season` (
  `start_date` varchar(10) NOT NULL,
  `end_date` varchar(10) NOT NULL,
  `ss` int NOT NULL,
  `is_enable` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`start_date`, `end_date`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
筛选is_enable = 1的所有数据，按ss倒序排序，返回数据. 
查出的数据,按key=ss,value={start_date: "xxx",end_date: "xxx", ss: xx} 缓存到内存xd_torchlight_season_cache中，1小时失效一次
### 返回数据说明
[
    {
        start_date: "20260101",
        end_date: "20260130",
        ss: 12
    }
]

## query_xd_torchlight_seasons_steam_players
查询执行赛季游戏峰值玩家
### path
/games/torchlight/seasons/players
### 接收参数
seasons list[int] 不能为空 格式["1,2,3"]
steam_id int 不能为空 只能是[2315040, 1974050]
### 处理逻辑
数据来源：远程MySQL表
CREATE TABLE `xd_game_steam_players` (
  `stat_ts` bigint NOT NULL COMMENT '统计时间',
  `type` varchar(20) NOT NULL COMMENT '时间类型',
  `peak_players` int NOT NULL COMMENT '峰值玩家',
  `steam_id` int NOT NULL COMMENT 'SteamID',
  PRIMARY KEY (`steam_id`, `type`, `stat_ts`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci

首先，从xd_torchlight_season_cache查询出seasons对应的赛季信息，然后从xd_game_steam_players查询stat_ts是时间戳，首先要将赛季start_date，end_date转换为utc时区的时间戳，然后筛选出stat_ts在start_date和end_date之间的数据(包含)，查询到的数据，计算ss_day: stat_ts - 赛季的开始时间utc时间戳 间隔多少天，第一天为1。返回的字段ss_day，ss, steam_id, peak_players, 再对其按ss, ss_day, steam_id groupby，取MAX(peak_players), 最后返回 ss_day，ss, steam_id, peak_players。

### 返回数据说明
[
    {
        ss: 12,
        ss_day: 1,
        steam_id: 123454,
        peak_players: 100
    }
]

