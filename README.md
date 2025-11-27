# keyword_filter · AstrBot 插件  

一个用于 **自定义屏蔽消息内容** 的 AstrBot 插件，支持三种匹配方式：  
- **前缀匹配**（消息以某些字符串开头 → 屏蔽）  
- **关键字匹配**（消息包含某些内容 → 屏蔽）  
- **后缀匹配**（消息以某些字符串结尾 → 屏蔽）

适用于内容过滤、群管辅助、自动忽略噪音消息等场景。

---

## 功能特性

- **前缀屏蔽**：例如 `#`、`/ai`、`BOT:`  
- **关键字屏蔽**：例如 `广告`、`违规词`、`无意义刷屏`  
- **后缀屏蔽**：例如 `.jpg`、`.mp4`、`)机器人`  
- **命令动态添加/删除屏蔽规则**  
- **配置自动持久化**，Bot 重启不丢失  

---

## 指令说明（管理屏蔽规则）

### 查看当前屏蔽规则

```
block_list
```

---

### 添加规则

```
block_add prefix <内容>
block_add keyword <内容>
block_add suffix <内容>
```

示例：

```
block_add prefix #
block_add keyword 广告
block_add suffix .jpg
```

---

### 删除规则

```
block_remove prefix <内容>
block_remove keyword <内容>
block_remove suffix <内容>
```

示例：

```
block_remove keyword 广告
block_remove prefix /
block_remove suffix .png
```
---

## 官方文档

[帮助文档](https://astrbot.app)