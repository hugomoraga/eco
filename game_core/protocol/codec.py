from __future__ import annotations

import json
from typing import Any

from game_core.protocol.messages import (
    ActionCommand,
    ErrorEvent,
    GameEvent,
    MessageType,
    QueryCommand,
    QueryResponseEvent,
    QueryType,
    QuitCommand,
    TerminatedEvent,
    TurnEndEvent,
    TurnStartEvent,
    WorldStateEvent,
    ActionResultEvent,
    CrisisEvent,
    TickEvent,
    UnionMessage,
    CircleActivityEvent,
    NPcActionEvent,
)


def encode(msg: UnionMessage) -> str:
    return json.dumps(msg.to_dict(), ensure_ascii=False)


def encode_many(msgs: list[UnionMessage]) -> str:
    return "\n".join(encode(msg) for msg in msgs)


def decode(raw: str) -> UnionMessage | dict | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    msg_type = data.get("type")
    if not msg_type:
        return None

    try:
        mt = MessageType(msg_type)
    except ValueError:
        return ErrorEvent(message=f"Unknown message type: {msg_type}").to_dict()

    if mt == MessageType.ACTION:
        return ActionCommand(
            turn=data.get("turn", 0),
            action=data.get("action", ""),
        )

    elif mt == MessageType.QUERY:
        qt = QueryType(data.get("query_type", "world_state"))
        return QueryCommand(
            query_id=data.get("query_id", ""),
            query_type=qt,
            params=data.get("params", {}),
        )

    elif mt == MessageType.QUIT:
        return QuitCommand()

    elif mt == MessageType.READY:
        return _decode_ready(data)

    elif mt == MessageType.TURN_START:
        return TurnStartEvent(
            turn=data.get("turn", 0),
            world_tick=data.get("world_tick", 0),
            world_state=data.get("world_state", {}),
        )

    elif mt == MessageType.ACTION_RESULT:
        return ActionResultEvent(
            turn=data.get("turn", 0),
            action=data.get("action", ""),
            success=data.get("success", False),
            message=data.get("message", ""),
            delta=data.get("delta", {}),
        )

    elif mt == MessageType.TURN_END:
        return TurnEndEvent(
            turn=data.get("turn", 0),
            world_tick=data.get("world_tick", 0),
            action_taken=data.get("action_taken"),
        )

    elif mt == MessageType.EVENT:
        return GameEvent(
            turn=data.get("turn", 0),
            event_type=data.get("event_type", ""),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
        )

    elif mt == MessageType.QUERY_RESPONSE:
        qt = QueryType(data.get("query_type", "world_state"))
        return QueryResponseEvent(
            query_id=data.get("query_id", ""),
            query_type=qt,
            data=data.get("data", {}),
        )

    elif mt == MessageType.CRISIS:
        return CrisisEvent(
            turn=data.get("turn", 0),
            metric=data.get("metric", ""),
            value=data.get("value", 0.0),
        )

    elif mt == MessageType.WORLD_STATE:
        return WorldStateEvent(
            turn=data.get("turn", 0),
            civ=data.get("civ", {}),
            echo=data.get("echo", {}),
            metrics=data.get("metrics", {}),
            entities=data.get("entities", {}),
        )

    elif mt == MessageType.TICK:
        return TickEvent(
            turn=data.get("turn", 0),
            world_tick=data.get("world_tick", 0),
            action_result=data.get("action_result"),
        )

    elif mt == MessageType.TERMINATED:
        return TerminatedEvent(reason=data.get("reason", ""))

    elif mt == MessageType.ERROR:
        return ErrorEvent(message=data.get("message", ""))

    elif mt == MessageType.CIRCLE_ACTIVITY:
        return CircleActivityEvent(
            turn=data.get("turn", 0),
            circle_name=data.get("circle_name", ""),
            activity=data.get("activity", ""),
        )

    elif mt == MessageType.NPC_ACTION:
        return NPcActionEvent(
            turn=data.get("turn", 0),
            npc_name=data.get("npc_name", ""),
            action=data.get("action", ""),
            message=data.get("message", ""),
            success=data.get("success", True),
        )

    return ErrorEvent(message=f"Unhandled message type: {msg_type}")


def _decode_ready(data: dict[str, Any]) -> dict[str, Any]:
    return data


def decode_command(raw: str) -> ActionCommand | QueryCommand | QuitCommand | ErrorEvent | None:
    msg = decode(raw)
    if isinstance(msg, (ActionCommand, QueryCommand, QuitCommand)):
        return msg
    if isinstance(msg, ErrorEvent):
        return msg
    if msg is None:
        return None
    return None
