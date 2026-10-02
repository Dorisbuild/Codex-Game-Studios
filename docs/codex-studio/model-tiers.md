# Codex models and role defaults

All shipped roles omit `model` and `model_reasoning_effort`, inheriting the
active parent's model and reasoning. Skills run in the selecting conversation
and have no model setting in their frontmatter.

A reusable project should not require a particular model or silently change
the user's cost/performance preference. Director/lead/specialist are workflow
responsibilities, not model aliases.

For an explicitly requested role customization, inspect current model access
and supported effort values before adding settings to that role's TOML. Run
the validator afterward. Model changes do not require rewriting skills.

[Official configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
