"""astrbot_plugin_btw

Initial scaffold for a /btw-style AstrBot plugin.
"""

from astrbot.api.star import Context, Star, register


@register("astrbot_plugin_btw", "PandragonXIII", "A /btw style side-question plugin for AstrBot.", "0.1.0")
class BTWPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
