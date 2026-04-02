from __future__ import annotations

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_btw",
    "PandragonXIII",
    "A /btw style side-question plugin for AstrBot.",
    "0.1.0",
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

    def _get_int(self, key: str, default: int) -> int:
        value = self.config.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _build_prompt(self, question: str) -> str:
        concise = self._get_bool("concise_mode", True)
        max_sentences = self._get_int("max_sentences", 4)
        include_prefix = self._get_bool("prefix_reply", True)

        style_lines = [
            "You are handling a temporary side question inside an ongoing conversation.",
            "Answer the user's question clearly and as independently as possible.",
            "Do not overuse unrelated prior context unless it is truly necessary.",
            "Do not redefine the main discussion topic.",
        ]

        if concise:
            style_lines.append(
                f"Keep the answer concise, ideally within {max_sentences} sentences."
            )

        if include_prefix:
            style_lines.append(
                "Start the answer with '[btw] ' to make the side-thread nature explicit."
            )

        style_lines.append("")
        style_lines.append("Side question:")
        style_lines.append(question.strip())
        return "\n".join(style_lines)

    @filter.command("btw")
    async def btw(self, event: AstrMessageEvent):
        """Handle /btw side questions with light prompt-layer isolation."""
        raw_text = (event.message_str or "").strip()
        parts = raw_text.split(maxsplit=1)

        if len(parts) < 2 or not parts[1].strip():
            yield event.plain_result(
                "用法：/btw <问题>\n例如：/btw HTTP 403 是什么？"
            )
            return

        question = parts[1].strip()
        prompt = self._build_prompt(question)

        try:
            provider_id = await self.context.get_current_chat_provider_id(
                umo=event.unified_msg_origin
            )
            llm_resp = await self.context.llm_generate(
                chat_provider_id=provider_id,
                prompt=prompt,
            )
            text = (getattr(llm_resp, "completion_text", "") or "").strip()
            if not text:
                text = "[btw] 没生成有效回复。"
            yield event.plain_result(text)
        except Exception as exc:
            logger.exception("[astrbot_plugin_btw] /btw failed")
            yield event.plain_result(f"[btw] 处理失败：{exc}")
