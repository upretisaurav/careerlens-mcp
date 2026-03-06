"""Agentic chat orchestration and streaming responses."""

import json
from collections.abc import AsyncIterator
from typing import Any

from app.tool_executor import execute_tool
from app.tools_config import CLAUDE_TOOLS, SYSTEM_PROMPT


def build_system_prompt(profile: dict[str, Any] | None) -> str:
    """Build system prompt with optional user profile context."""
    system = SYSTEM_PROMPT
    if not profile:
        return system

    context_lines = ["\n\n--- USER PROFILE (pre-filled context) ---"]
    if profile.get("role"):
        context_lines.append(f"Role: {profile['role']}")
    if profile.get("location"):
        context_lines.append(f"Location: {profile['location']}")
    if profile.get("skills"):
        context_lines.append(f"Skills: {', '.join(profile['skills'])}")
    if profile.get("current_salary"):
        context_lines.append(f"Current salary: ${profile['current_salary']:,}")
    if profile.get("years_of_experience"):
        context_lines.append(f"Years of experience: {profile['years_of_experience']}")

    return system + "\n".join(context_lines)


async def stream_agentic_response(
    client: Any,
    system: str,
    messages: list[dict[str, Any]],
) -> AsyncIterator[str]:
    """Run Claude agentic loop and stream SSE events."""
    current_messages = messages.copy()

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=system,
            tools=CLAUDE_TOOLS,
            messages=current_messages,
        )

        tool_calls = [block for block in response.content if block.type == "tool_use"]
        text_blocks = [block for block in response.content if block.type == "text"]

        for block in text_blocks:
            if block.text.strip():
                yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"

        if response.stop_reason == "end_turn" or not tool_calls:
            break

        tool_results = []
        for tool_call in tool_calls:
            start_event = {
                "type": "tool_start",
                "tool": tool_call.name,
                "input": tool_call.input,
            }
            yield (f"data: {json.dumps(start_event)}\n\n")

            result_str = await execute_tool(tool_call.name, tool_call.input)
            result_data = json.loads(result_str)

            result_event = {
                "type": "tool_result",
                "tool": tool_call.name,
                "result": result_data,
            }
            yield (f"data: {json.dumps(result_event)}\n\n")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result_str,
                }
            )

        current_messages.append({"role": "assistant", "content": response.content})
        current_messages.append({"role": "user", "content": tool_results})

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
