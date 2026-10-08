#!/usr/bin/env python3
"""Testbed runner interface (paper Section VII) -- INTERFACE ONLY, NOT IMPLEMENTED.

This module defines the contract a model runner and a benign channel probe must
satisfy for the contained, air-gapped evaluation described in the paper. It is
intentionally unimplemented: wiring it to live models and running an elicitation
study is the authors' experiment, to be conducted under institutional safety
review in an environment with no outbound network and no real credentials.

The configured cohort is Claude models only for the initial study (see
`models.json`). A benign "channel" here is an operator-planted marker used to
measure whether one run can observe another's trace; it carries no payload and
no exploit.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class Task:
    task_id: str
    tier: str          # "solvable" | "hard" | "impossible"
    prompt: str
    abstention_ok: bool  # whether "cannot be done" is scored as success (condition-dependent)


@dataclass
class RunResult:
    run_id: str
    task_id: str
    model: str
    abstained: bool
    transcript_path: str
    event_log_path: str   # JSONL consumed by monitor/shared_write_monitor.py


class AgentRunner(abc.ABC):
    """Runs one agent on one task inside the sandbox and records an event log."""

    @abc.abstractmethod
    def run(self, task: Task, run_id: str, model: str, condition: str) -> RunResult:
        raise NotImplementedError(
            "Not implemented in this public release. Provide a sandboxed runner "
            "that executes only inside the air-gapped testbed; see README and "
            "SECURITY.md."
        )


class ChannelProbe(abc.ABC):
    """Plants a benign marker as one run and checks whether another run can read it.

    Implementations MUST operate only on operator-provided, non-functional
    markers inside the testbed, and MUST NOT encode or relay task data.
    """

    @abc.abstractmethod
    def plant(self, run_id: str, marker: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def observed_by(self, run_id: str) -> bool:
        raise NotImplementedError
