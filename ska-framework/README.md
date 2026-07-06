# Structured Knowledge Accumulation (SKA)

The AI Agent Farm treats every exchange — between agents, and between humans and
agents — as a timestamped, structured knowledge event. Each event reduces
informational entropy and is stored in QuestDB in forward-only order, so the
system accumulates specialized expertise without retraining. These are the two
channels through which that accumulation happens:

- **[agent-agent-knowledge](agent-agent-knowledge/)** — agent ↔ agent communication
  with knowledge extraction. Messages flow through a single database loop
  (raw message + structured knowledge), a notifier pings the recipient, and
  collective intelligence emerges without an orchestration layer.

- **[human-agent-knowledge](human-agent-knowledge/)** — human ↔ agent
  conversation-as-telemetry. Terminal sessions are logged, parsed, and streamed
  into QuestDB, giving the agent persistent, searchable memory across sessions.
  Includes production loggers for both real-time streaming and batch-session
  ingestion under [`human-agent-knowledge/production`](human-agent-knowledge/production/).

For the mathematical foundation behind this approach, see the
[SKA Framework documentation](https://github.com/quantiota/AI-Agent-Host/tree/main/ska-framework/).

## Paper

Bouarfa Mahi, *Structured Knowledge Accumulation: A Standard AI Infrastructure
for Studying Forward-Only Learning through Knowledge Accumulation in LLMs*,
Quantiota. TechRxiv.
[doi:10.36227/techrxiv.176282131.11209360/v1](https://doi.org/10.36227/techrxiv.176282131.11209360/v1)
— [local PDF](papers/techrxiv.176282131.11209360_v1.pdf)
