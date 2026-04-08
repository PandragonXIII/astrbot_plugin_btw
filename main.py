from __future__ import annotations

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_btw",
    "PandragonXIII",
    "A /btw style side-question plugin for AstrBot.",
    "0.1.1",
)
class BTWPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = context.get_config()

    def _get_bool(self, key: str, default: bool) -> bool:
        value = self.config.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    @filter.command("btw")
    async def btw(self, event: AstrMessageEvent):
        """Ask a side question via a separate llm_generate call."""
        raw_text = (event.message_str or "").strip()
        parts = raw_text.split(maxsplit=1)

        if len(parts) < 2 or not parts[1].strip():
            yield event.plain_result(
                "用法：/btw <问题>\n例如：/btw HTTP 403 是什么？"
            )
            return

        question = parts[1].strip()
        add_prefix = self._get_bool("prefix_reply", True)

        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            llm_resp = await self.context.llm_generate(
                chat_provider_id=provider_id,
                prompt=question,
            )
            text = (getattr(llm_resp, "completion_text", "") or "").strip()
            if not text:
                text = "没生成有效回复。"
            if add_prefix:
                text = f"[btw] {text}"
            yield event.plain_result(text)
        except Exception as exc:
            logger.exception("[astrbot_plugin_btw] /btw failed")
            yield event.plain_result(f"[btw] 处理失败：{exc}")
