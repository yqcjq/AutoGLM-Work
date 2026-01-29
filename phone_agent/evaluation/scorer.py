"""Task scorer module.

This module provides task execution quality evaluation functionality,
using LLM to score task execution from multiple dimensions.
"""

import json
from dataclasses import dataclass
from typing import Any

from phone_agent.config.scoring_prompts_en import (
    SCORING_SYSTEM_PROMPT as SCORING_SYSTEM_PROMPT_EN,
    SCORING_USER_PROMPT_TEMPLATE as SCORING_USER_PROMPT_TEMPLATE_EN,
)
from phone_agent.config.scoring_prompts_zh import (
    SCORING_SYSTEM_PROMPT as SCORING_SYSTEM_PROMPT_ZH,
    SCORING_USER_PROMPT_TEMPLATE as SCORING_USER_PROMPT_TEMPLATE_ZH,
)
from phone_agent.model import ModelClient
from phone_agent.model.client import MessageBuilder


@dataclass
class ScoringConfig:
    """Scoring configuration."""

    enabled: bool = True
    lang: str = "cn"
    max_context_steps: int = 50  # Maximum context steps
    timeout: float = 30.0  # Timeout in seconds


@dataclass
class ScoreResult:
    """Scoring result."""

    completion_quality: dict[str, Any]  # {"score": int, "reasoning": str}
    efficiency: dict[str, Any]
    logic: dict[str, Any]
    overall_score: float
    summary: str
    suggestions: list[str]
    raw_response: str
    success: bool
    error_message: str | None = None


class TaskScorer:
    """
    Task execution quality evaluator.

    Uses LLM to analyze complete task execution context and score from dimensions:
    - Completion Quality: Accuracy and completeness of task completion
    - Efficiency: Reasonableness of step count and path selection
    - Logic: Correctness of reasoning process and operation sequence
    """

    def __init__(
        self,
        model_client: ModelClient,
        config: ScoringConfig | None = None,
    ):
        """
        Initialize the scorer.

        Args:
            model_client: Model client for scoring requests.
            config: Scoring configuration.
        """
        self.model_client = model_client
        self.config = config or ScoringConfig()

    def score_task(
        self,
        task_description: str,
        execution_context: list[dict[str, Any]],
        success: bool,
        final_message: str,
        total_steps: int,
    ) -> ScoreResult:
        """
        Evaluate completed task execution.

        Args:
            task_description: Original task description.
            execution_context: List of execution steps with thinking and action.
            success: Whether task completed successfully.
            final_message: Final message.
            total_steps: Total number of steps.

        Returns:
            ScoreResult object with evaluation scores and feedback.
        """
        if not self.config.enabled:
            return self._create_disabled_result()

        try:
            # 构建评分提示
            scoring_messages = self._build_scoring_messages(
                task_description=task_description,
                execution_context=execution_context,
                success=success,
                final_message=final_message,
                total_steps=total_steps,
            )

            # 请求模型评分
            response = self.model_client.request(scoring_messages)

            # 解析评分响应
            score_result = self._parse_scoring_response(response.raw_content)
            score_result.raw_response = response.raw_content
            score_result.success = True

            return score_result

        except Exception as e:
            return ScoreResult(
                completion_quality={"score": 0, "reasoning": "评分失败"},
                efficiency={"score": 0, "reasoning": "评分失败"},
                logic={"score": 0, "reasoning": "评分失败"},
                overall_score=0.0,
                summary="评分失败",
                suggestions=[],
                raw_response="",
                success=False,
                error_message=str(e),
            )

    def _build_scoring_messages(
        self,
        task_description: str,
        execution_context: list[dict[str, Any]],
        success: bool,
        final_message: str,
        total_steps: int,
    ) -> list[dict[str, Any]]:
        """Build messages for scoring request."""
        # 根据语言获取提示词
        if self.config.lang == "en":
            system_prompt = SCORING_SYSTEM_PROMPT_EN
            user_template = SCORING_USER_PROMPT_TEMPLATE_EN
            status_text = "Success" if success else "Failed"
        else:
            system_prompt = SCORING_SYSTEM_PROMPT_ZH
            user_template = SCORING_USER_PROMPT_TEMPLATE_ZH
            status_text = "成功" if success else "失败"

        # 从上下文构建执行详情
        execution_details = self._format_execution_details(
            execution_context, self.config.max_context_steps
        )

        # 格式化用户提示
        user_prompt = user_template.format(
            task_description=task_description,
            status=status_text,
            total_steps=total_steps,
            final_message=final_message,
            execution_details=execution_details,
        )

        return [
            MessageBuilder.create_system_message(system_prompt),
            MessageBuilder.create_user_message(user_prompt),
        ]

    def _format_execution_details(
        self, execution_context: list[dict[str, Any]], max_steps: int
    ) -> str:
        """Format execution context into readable text."""
        details = []

        # 限制为最近的max_steps步
        steps_to_include = (
            execution_context[-max_steps:]
            if len(execution_context) > max_steps
            else execution_context
        )

        for i, step in enumerate(steps_to_include, 1):
            if "thinking" in step and "action" in step:
                details.append(f"### 步骤 {step.get('step', i)}")
                # 截断过长的思考过程
                thinking = step["thinking"]
                if len(thinking) > 200:
                    thinking = thinking[:200] + "..."
                details.append(f"**思考**: {thinking}")
                details.append(f"**操作**: {step['action']}")
                if "result" in step:
                    result_info = step["result"]
                    if isinstance(result_info, dict):
                        success_str = "成功" if result_info.get("success") else "失败"
                        details.append(f"**结果**: {success_str}")
                        if result_info.get("message"):
                            details.append(f"**消息**: {result_info['message']}")
                    else:
                        details.append(f"**结果**: {result_info}")
                details.append("")

        return "\n".join(details)

    def _parse_scoring_response(self, response: str) -> ScoreResult:
        """Parse JSON scoring response from model."""
        # 移除可能存在的markdown代码块标记
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # 解析JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"无法将评分响应解析为JSON: {e}")

        # 验证并提取字段
        return ScoreResult(
            completion_quality=data.get(
                "completion_quality", {"score": 0, "reasoning": ""}
            ),
            efficiency=data.get("efficiency", {"score": 0, "reasoning": ""}),
            logic=data.get("logic", {"score": 0, "reasoning": ""}),
            overall_score=float(data.get("overall_score", 0.0)),
            summary=data.get("summary", ""),
            suggestions=data.get("suggestions", []),
            raw_response=response,
            success=True,
        )

    def _create_disabled_result(self) -> ScoreResult:
        """Create result when scoring is disabled."""
        return ScoreResult(
            completion_quality={"score": 0, "reasoning": "评分已禁用"},
            efficiency={"score": 0, "reasoning": "评分已禁用"},
            logic={"score": 0, "reasoning": "评分已禁用"},
            overall_score=0.0,
            summary="评分已禁用",
            suggestions=[],
            raw_response="",
            success=False,
            error_message="评分功能已禁用",
        )
