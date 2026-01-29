"""Logger for recording agent execution details."""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class LogConfig:
    """Configuration for the logger."""

    log_dir: str = "logs"
    enable_model_log: bool = True
    enable_action_log: bool = True


class AgentLogger:
    """
    Logger for recording agent execution details.

    Creates two log files per session:
    1. Model log: Records full model responses (thinking + action)
    2. Action log: Records only the parsed action objects
    """

    def __init__(self, config: LogConfig | None = None, session_name: str | None = None, model_config: dict[str, Any] | None = None):
        """
        Initialize the logger.

        Args:
            config: Logger configuration.
            session_name: Optional custom session name. If not provided, uses timestamp.
            model_config: Optional model configuration to include in logs.
        """
        self.config = config or LogConfig()
        self.model_config = model_config or {}

        # Create log directory
        self.log_dir = Path(self.config.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate session ID and filenames
        if session_name:
            self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_name}"
        else:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.model_log_path = self.log_dir / f"{self.session_id}_model.jsonl"
        self.action_log_path = self.log_dir / f"{self.session_id}_actions.jsonl"

        # Initialize log files with metadata
        self._initialize_logs()

    def _initialize_logs(self) -> None:
        """Initialize log files with session metadata."""
        metadata = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "log_type": None,
            "model_config": self.model_config,
        }

        if self.config.enable_model_log:
            model_metadata = metadata.copy()
            model_metadata["log_type"] = "model_responses"
            self._write_to_file(self.model_log_path, model_metadata)

        if self.config.enable_action_log:
            action_metadata = metadata.copy()
            action_metadata["log_type"] = "actions"
            self._write_to_file(self.action_log_path, action_metadata)

    def log_model_response(
        self,
        step: int,
        thinking: str,
        action: str,
        raw_content: str,
        time_to_first_token: float | None = None,
        time_to_thinking_end: float | None = None,
        total_time: float | None = None,
    ) -> None:
        """
        Log a model response.

        Args:
            step: Step number.
            thinking: Thinking process from the model.
            action: Action string from the model.
            raw_content: Raw response content.
            time_to_first_token: Time to first token in seconds.
            time_to_thinking_end: Time to thinking end in seconds.
            total_time: Total inference time in seconds.
        """
        if not self.config.enable_model_log:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "thinking": thinking,
            "action": action,
            "raw_content": raw_content,
            "performance": {
                "time_to_first_token": time_to_first_token,
                "time_to_thinking_end": time_to_thinking_end,
                "total_time": total_time,
            },
        }

        self._write_to_file(self.model_log_path, log_entry)

    def log_action(
        self,
        step: int,
        action: dict[str, Any],
        success: bool,
        message: str | None = None,
        screen_info: dict[str, Any] | None = None,
    ) -> None:
        """
        Log an action execution.

        Args:
            step: Step number.
            action: Parsed action dictionary.
            success: Whether the action executed successfully.
            message: Optional result message.
            screen_info: Optional screen information (current app, dimensions, etc).
        """
        if not self.config.enable_action_log:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "action": action,
            "result": {
                "success": success,
                "message": message,
            },
            "screen_info": screen_info or {},
        }

        self._write_to_file(self.action_log_path, log_entry)

    def log_task_start(self, task: str) -> None:
        """
        Log the start of a task.

        Args:
            task: Task description.
        """
        log_entry = {
            "event": "task_start",
            "timestamp": datetime.now().isoformat(),
            "task": task,
        }

        if self.config.enable_model_log:
            self._write_to_file(self.model_log_path, log_entry)

        if self.config.enable_action_log:
            self._write_to_file(self.action_log_path, log_entry)

    def log_task_end(self, success: bool, message: str | None = None, total_steps: int = 0) -> None:
        """
        Log the end of a task.

        Args:
            success: Whether the task completed successfully.
            message: Final message.
            total_steps: Total number of steps executed.
        """
        log_entry = {
            "event": "task_end",
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "message": message,
            "total_steps": total_steps,
        }

        if self.config.enable_model_log:
            self._write_to_file(self.model_log_path, log_entry)

        if self.config.enable_action_log:
            self._write_to_file(self.action_log_path, log_entry)

    def log_scoring(self, score_result: Any) -> None:
        """
        Log task scoring results.

        Args:
            score_result: ScoreResult object with evaluation scores.
        """
        log_entry = {
            "event": "task_scoring",
            "timestamp": datetime.now().isoformat(),
            "scoring": {
                "success": score_result.success,
                "completion_quality": score_result.completion_quality,
                "efficiency": score_result.efficiency,
                "logic": score_result.logic,
                "overall_score": score_result.overall_score,
                "summary": score_result.summary,
                "suggestions": score_result.suggestions,
            },
        }

        if not score_result.success:
            log_entry["scoring"]["error"] = score_result.error_message

        # Write to both logs
        if self.config.enable_model_log:
            self._write_to_file(self.model_log_path, log_entry)

        if self.config.enable_action_log:
            self._write_to_file(self.action_log_path, log_entry)

    def _write_to_file(self, file_path: Path, data: dict[str, Any]) -> None:
        """
        Write a log entry to file.

        Args:
            file_path: Path to the log file.
            data: Data to write.
        """
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                # Always write compact JSON for JSONL format
                # pretty_json option is ignored to maintain JSONL compatibility
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"Warning: Failed to write log to {file_path}: {e}")

    def get_log_summary(self) -> dict[str, Any]:
        """
        Get a summary of the current logging session.

        Returns:
            Dictionary with log file paths and statistics.
        """
        summary = {
            "session_id": self.session_id,
            "model_log": str(self.model_log_path) if self.config.enable_model_log else None,
            "action_log": str(self.action_log_path) if self.config.enable_action_log else None,
        }

        # Count entries in each log
        if self.config.enable_model_log and self.model_log_path.exists():
            with open(self.model_log_path, "r", encoding="utf-8") as f:
                summary["model_log_entries"] = sum(1 for _ in f)

        if self.config.enable_action_log and self.action_log_path.exists():
            with open(self.action_log_path, "r", encoding="utf-8") as f:
                summary["action_log_entries"] = sum(1 for _ in f)

        return summary
