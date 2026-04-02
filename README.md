# astrbot_plugin_btw

An AstrBot plugin that brings a Claude Code-like `/btw <question>` experience into chat: a lightweight side query that is intentionally isolated from the main ongoing topic.

## Goal

In real conversations, users often want to ask a small unrelated question without polluting the current context. This plugin is meant to provide a simple `/btw` command so the assistant can answer a side question in a more isolated and self-contained way.

## Core Idea

`/btw <question>` should be treated as a **temporary side thread** inside the current conversation.

Expected behavior:
- The user can ask a short off-topic question without fully switching the main topic.
- The assistant should answer the `/btw` question in a compact, self-contained style.
- The answer should avoid dragging too much of the current conversation context into the side reply unless necessary.
- After the `/btw` answer, the conversation should naturally return to the main topic.

## Confirmed API Basis

Based on the AstrBot docs, the v1 implementation can rely on two core capabilities:

1. **Registering a command with `@filter.command("btw")`**
2. **Calling the current chat model with `self.context.llm_generate(...)`**

Relevant docs:
- Command registration: https://docs.astrbot.app/dev/star/guides/simple.html
- AI / LLM call: https://docs.astrbot.app/dev/star/guides/ai.html

## What the docs confirm

### 1) Command registration
AstrBot supports registering a command handler like this:

```python
@filter.command("helloworld")
async def helloworld(self, event: AstrMessageEvent):
    yield event.plain_result("Hello!")
```

So the `/btw` entry point in v1 can be implemented as:

```python
@filter.command("btw")
async def btw(self, event: AstrMessageEvent):
    ...
```

### 2) Calling the current session's LLM
AstrBot supports fetching the current provider ID from the current unified message origin:

```python
umo = event.unified_msg_origin
provider_id = await self.context.get_current_chat_provider_id(umo=umo)
```

Then calling the model directly:

```python
llm_resp = await self.context.llm_generate(
    chat_provider_id=provider_id,
    prompt="Hello, world!",
)
```

This is enough to support a minimal `/btw` implementation.

### 3) Optional future extension: conversation management
The AI guide also exposes the conversation manager, including methods such as:
- `get_curr_conversation_id`
- `get_conversation`
- `new_conversation`
- `switch_conversation`

This is important because it means future versions may explore stronger isolation strategies. However, v1 does **not** need to claim true session isolation if it only uses prompt-layer isolation.

## V1 Implementation Strategy

The first usable version should use **prompt-layer isolation** rather than fake hidden session splitting.

Planned flow:

1. User sends `/btw <question>`
2. Plugin extracts the side question text
3. Plugin gets the current chat provider ID via `event.unified_msg_origin`
4. Plugin builds a constrained prompt, for example:
   - this is a side question
   - answer briefly and independently
   - avoid overusing the current main-topic context unless necessary
   - do not treat this as a full topic switch
5. Plugin calls `self.context.llm_generate(...)`
6. Plugin returns the generated text as the `/btw` reply

## Suggested prompt behavior for v1

The prompt wrapper should explicitly instruct the model to:
- treat the input as a temporary side question
- answer in a concise and self-contained way
- avoid dragging in unrelated prior context
- avoid reframing the whole conversation topic
- return directly useful content

A representative prompt shape might be:

```text
You are handling a temporary side question inside an ongoing conversation.
Answer the user's question briefly and clearly.
Keep the answer as self-contained as possible.
Do not overuse the previous main-topic context unless it is truly necessary.
After answering, do not try to redefine the main discussion.

Side question:
{question}
```

## Why this is enough for v1

This approach is honest and implementable:
- it uses documented AstrBot APIs
- it avoids pretending to create a real isolated hidden chat session
- it already captures the main user value of `/btw`: a quick off-topic detour with reduced context pollution

## Design Principles

1. **Context isolation, not context amnesia**  
   `/btw` is not a brand new session. It is a constrained side query inside the same conversation. The plugin should reduce irrelevant carry-over, while still keeping enough context to remain coherent when needed.

2. **Short and practical output**  
   `/btw` is intended for quick detours, not long-form mode switching.

3. **Low surprise**  
   Users should be able to understand what the plugin is doing. If special handling is applied, the behavior should stay predictable.

4. **Safe fallback**  
   If strict isolation is not technically possible under current AstrBot capabilities, the plugin should fall back to a prompt-level isolation strategy instead of pretending to create a real separate hidden session.

## Possible Future Directions

### Option A: Better prompt isolation
Refine the isolation prompt and output constraints.

### Option B: Controlled conversation-context narrowing
Use conversation APIs to inspect history and selectively pass a narrowed context window.

### Option C: Temporary mini-conversation mode
Explore whether a temporary conversation can be created and queried without polluting the active thread state.
This should only be done if AstrBot's APIs make the behavior explicit and reliable.

## Expected Command Form

```text
/btw 今晚吃什么
/btw What does HTTP 403 mean?
```

## Non-goals (for v1)

- Full multi-thread conversation management
- Persistent side-thread history
- Complex UI state switching
- Pretending to provide guaranteed memory isolation when only prompt isolation is implemented

## Development Notes

- Follow AstrBot plugin conventions.
- Keep plugin metadata clear.
- Add config support only when actually needed.
- Prefer a small but honest v1 over an overengineered fake isolation design.

## Validation Notes

- `/btw` has been validated in a live AstrBot environment.
- A test query like `/btw What does HTTP 403 mean?` successfully triggered an isolated side-question style response.
- The current implementation is still prompt-layer isolation, but it already delivers the intended lightweight detour experience in practice.

## Current Status

- Repository initialized
- MIT license added
- README implementation plan updated based on official docs
- V1 command implementation completed
- Basic local deployment test passed in AstrBot
- `/btw What does HTTP 403 mean?` was successfully used as a validation example
