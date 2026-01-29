"""Configuration module for Phone Agent."""

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.config.apps_ios import APP_PACKAGES_IOS
from phone_agent.config.i18n import get_message, get_messages
from phone_agent.config.prompts_en import SYSTEM_PROMPT as SYSTEM_PROMPT_EN
from phone_agent.config.prompts_zh import SYSTEM_PROMPT as SYSTEM_PROMPT_ZH
from phone_agent.config.scoring_prompts_en import (
    SCORING_SYSTEM_PROMPT as SCORING_SYSTEM_PROMPT_EN,
    SCORING_USER_PROMPT_TEMPLATE as SCORING_USER_PROMPT_TEMPLATE_EN,
)
from phone_agent.config.scoring_prompts_zh import (
    SCORING_SYSTEM_PROMPT as SCORING_SYSTEM_PROMPT_ZH,
    SCORING_USER_PROMPT_TEMPLATE as SCORING_USER_PROMPT_TEMPLATE_ZH,
)
from phone_agent.config.timing import (
    TIMING_CONFIG,
    ActionTimingConfig,
    ConnectionTimingConfig,
    DeviceTimingConfig,
    TimingConfig,
    get_timing_config,
    update_timing_config,
)


def get_system_prompt(lang: str = "cn") -> str:
    """
    Get system prompt by language.

    Args:
        lang: Language code, 'cn' for Chinese, 'en' for English.

    Returns:
        System prompt string.
    """
    if lang == "en":
        return SYSTEM_PROMPT_EN
    return SYSTEM_PROMPT_ZH


# Default to Chinese for backward compatibility
SYSTEM_PROMPT = SYSTEM_PROMPT_ZH


def get_scoring_prompts(lang: str = "cn") -> tuple[str, str]:
    """
    Get scoring prompts by language.

    Args:
        lang: Language code, 'cn' for Chinese, 'en' for English.

    Returns:
        Tuple of (system_prompt, user_template).
    """
    if lang == "en":
        return SCORING_SYSTEM_PROMPT_EN, SCORING_USER_PROMPT_TEMPLATE_EN
    return SCORING_SYSTEM_PROMPT_ZH, SCORING_USER_PROMPT_TEMPLATE_ZH


__all__ = [
    "APP_PACKAGES",
    "APP_PACKAGES_IOS",
    "SYSTEM_PROMPT",
    "SYSTEM_PROMPT_ZH",
    "SYSTEM_PROMPT_EN",
    "get_system_prompt",
    "SCORING_SYSTEM_PROMPT_ZH",
    "SCORING_SYSTEM_PROMPT_EN",
    "SCORING_USER_PROMPT_TEMPLATE_ZH",
    "SCORING_USER_PROMPT_TEMPLATE_EN",
    "get_scoring_prompts",
    "get_messages",
    "get_message",
    "TIMING_CONFIG",
    "TimingConfig",
    "ActionTimingConfig",
    "DeviceTimingConfig",
    "ConnectionTimingConfig",
    "get_timing_config",
    "update_timing_config",
]
