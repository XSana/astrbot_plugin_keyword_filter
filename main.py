from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig, logger


@register("keyword_filter", "XSana", "一个可自定义屏蔽前缀/关键字/后缀的插件", "1.0.0")
class KeywordBlocker(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        self.block_prefixes = self.config.get("block_prefixes") or []
        self.block_keywords = self.config.get("block_keywords") or []
        self.block_suffixes = self.config.get("block_suffixes") or []

        logger.info(
            f"关键词过滤配置已加载 | 前缀={len(self.block_prefixes)}, "
            f"关键字={len(self.block_keywords)}, 后缀={len(self.block_suffixes)}"
        )

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def filter_block_keywords(self, event: AstrMessageEvent):
        message_text = event.message_str or ""
        if not message_text:
            return None

        hit_category = None
        hit_rule = None

        for prefix in self.block_prefixes:
            if message_text.startswith(prefix):
                hit_category = "前缀"
                hit_rule = prefix
                break

        if hit_rule is None:
            for keyword in self.block_keywords:
                if keyword in message_text:
                    hit_category = "关键字"
                    hit_rule = keyword
                    break

        if hit_rule is None:
            for suffix in self.block_suffixes:
                if message_text.endswith(suffix):
                    hit_category = "后缀"
                    hit_rule = suffix
                    break

        if hit_rule is not None:
            logger.info(f"关键词过滤命中{hit_category} '{hit_rule}' | 消息: {message_text}")
            return event.stop_event()

        return None

    def _get_list_by_mode(self, mode: str):
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
        self.config["block_prefixes"] = self.block_prefixes
        self.config["block_keywords"] = self.block_keywords
        self.config["block_suffixes"] = self.block_suffixes
        self.config.save_config()


    @filter.command("block_list")
    async def show_block_list(self, event: AstrMessageEvent):
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

    @filter.command("block_add")
    async def add_block_rule(self, event: AstrMessageEvent):
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

        logger.info(
            f"关键词过滤新增{self._mode_human_name(mode)}规则: '{value}'"
        )
        yield event.plain_result(
            f"已在 {self._mode_human_name(mode)} 规则中添加：'{value}'"
        )

    @filter.command("block_remove")
    async def remove_block_rule(self, event: AstrMessageEvent):
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

        logger.info(
            f"关键词过滤移除{self._mode_human_name(mode)}规则: '{value}'"
        )
        yield event.plain_result(
            f"已从 {self._mode_human_name(mode)} 规则中移除：'{value}'"
        )