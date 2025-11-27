from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig, logger


@register("keyword_filter", "XSana", "一个可自定义屏蔽前缀/关键字/后缀的插件", "1.0.0")
class KeywordBlocker(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config  # AstrBotConfig 继承自 dict

        # 从配置中取出三种规则列表，如果没有就用空列表
        self.block_prefixes = self.config.get("block_prefixes") or []
        self.block_keywords = self.config.get("block_keywords") or []
        self.block_suffixes = self.config.get("block_suffixes") or []

        logger.info(
            f"[KeywordBlocker] 已加载屏蔽配置: "
            f"前缀={self.block_prefixes}, "
            f"关键字={self.block_keywords}, "
            f"后缀={self.block_suffixes}"
        )

    # ========== 核心过滤逻辑 ==========

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def filter_block_keywords(self, event: AstrMessageEvent):
        """根据前缀 / 关键字 / 后缀规则屏蔽消息"""
        message_text = event.message_str or ""

        # 前缀匹配：以某些字符串开头
        if any(message_text.startswith(p) for p in self.block_prefixes):
            logger.info(f"[KeywordBlocker] 前缀匹配命中，已屏蔽消息: {message_text}")
            return event.stop_event()

        # 关键字匹配：包含某些字符串
        if any(k in message_text for k in self.block_keywords):
            logger.info(f"[KeywordBlocker] 关键字匹配命中，已屏蔽消息: {message_text}")
            return event.stop_event()

        # 后缀匹配：以某些字符串结尾
        if any(message_text.endswith(s) for s in self.block_suffixes):
            logger.info(f"[KeywordBlocker] 后缀匹配命中，已屏蔽消息: {message_text}")
            return event.stop_event()

        return None

    # ========== 工具方法 ==========

    def _get_list_by_mode(self, mode: str):
        """根据模式字符串返回对应的列表引用"""
        if mode == "prefix":
            return self.block_prefixes
        if mode == "keyword":
            return self.block_keywords
        if mode == "suffix":
            return self.block_suffixes
        return None

    def _mode_human_name(self, mode: str) -> str:
        return {
            "prefix": "前缀",
            "keyword": "关键字",
            "suffix": "后缀",
        }.get(mode, mode)

    def _save_config(self):
        """同步内存到 AstrBotConfig 并持久化到磁盘"""
        self.config["block_prefixes"] = self.block_prefixes
        self.config["block_keywords"] = self.block_keywords
        self.config["block_suffixes"] = self.block_suffixes
        self.config.save_config()

    # ========== 命令：查看当前规则 ==========

    @filter.command("block_list")
    async def show_block_list(self, event: AstrMessageEvent):
        """显示当前屏蔽规则列表"""
        def fmt_list(title, items):
            if not items:
                return f"{title}: （空）"
            lines = "\n".join(f"- {i}" for i in items)
            return f"{title}:\n{lines}"

        msg = "\n\n".join([
            fmt_list("前缀屏蔽（prefix）", self.block_prefixes),
            fmt_list("关键字屏蔽（keyword）", self.block_keywords),
            fmt_list("后缀屏蔽（suffix）", self.block_suffixes),
        ])

        yield event.plain_result("当前屏蔽规则：\n" + msg)

    # ========== 命令：添加规则 ==========

    @filter.command("block_add")
    async def add_block_rule(self, event: AstrMessageEvent):
        """
        添加屏蔽规则
        用法：
        - block_add prefix <文本>
        - block_add keyword <文本>
        - block_add suffix <文本>
        """
        message_text = event.message_str or ""
        parts = message_text.split(maxsplit=2)

        if len(parts) < 3:
            yield event.plain_result(
                "用法：block_add <prefix|keyword|suffix> <文本>\n"
                "示例：block_add keyword 广告"
            )
            return

        mode = parts[1].strip().lower()
        value = parts[2].strip()

        lst = self._get_list_by_mode(mode)
        if lst is None:
            yield event.plain_result("模式错误，仅支持：prefix / keyword / suffix")
            return

        if value in lst:
            yield event.plain_result(
                f"{self._mode_human_name(mode)}规则中已存在：'{value}'"
            )
            return

        lst.append(value)
        self._save_config()

        logger.info(f"[KeywordBlocker] [{mode}] 新增屏蔽规则: {value}")
        yield event.plain_result(
            f"已在 {self._mode_human_name(mode)} 规则中添加：'{value}'"
        )

    # ========== 命令：移除规则 ==========

    @filter.command("block_remove")
    async def remove_block_rule(self, event: AstrMessageEvent):
        """
        移除屏蔽规则
        用法：
        - block_remove prefix <文本>
        - block_remove keyword <文本>
        - block_remove suffix <文本>
        """
        message_text = event.message_str or ""
        parts = message_text.split(maxsplit=2)

        if len(parts) < 3:
            yield event.plain_result(
                "用法：block_remove <prefix|keyword|suffix> <文本>\n"
                "示示例：block_remove keyword 广告"
            )
            return

        mode = parts[1].strip().lower()
        value = parts[2].strip()

        lst = self._get_list_by_mode(mode)
        if lst is None:
            yield event.plain_result("模式错误，仅支持：prefix / keyword / suffix")
            return

        if value not in lst:
            yield event.plain_result(
                f"{self._mode_human_name(mode)} 规则中不存在：'{value}'"
            )
            return

        lst.remove(value)
        self._save_config()

        logger.info(f"[KeywordBlocker] [{mode}] 移除屏蔽规则: {value}")
        yield event.plain_result(
            f"已从 {self._mode_human_name(mode)} 规则中移除：'{value}'"
        )