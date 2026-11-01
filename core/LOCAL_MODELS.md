# Local model trial (2026-10-31)

This machine has 8 GB RAM, an i7-8650U CPU, no discrete GPU, and was already using
4.5 GB of swap while kbrain ran. Ollama was installed but had no models. I pulled
`qwen3:1.7b-q4_K_M` (1.4 GB weights) and `qwen3:0.6b-q4_K_M` (523 MB weights).

| Probe | Result |
| --- | --- |
| 1.7B direct JSON, 2K context | 17 s for 48 output tokens. It explained its choice but returned an empty task list despite the required one task. |
| 1.7B constrained choice, 1K context | 11 s for 29 output tokens. It returned valid JSON and selected `none`; this is useful as a conservative triage signal, not as a final research decision. |
| 0.6B constrained choice, 1K context | 4 s for 42 output tokens. It returned valid JSON, but its reason mostly repeated the input. |
| 1.7B through OpenCode file tools, 4K context | Ollama reported a 1.9 GB loaded model; OpenCode used another ~350 MB. No file was written after a minute, so the probe was stopped. |

The local model is therefore **not in the live routing chain**. It is promising
for narrow extraction or ranking if the harness provides the candidate records
and validates the output. It did not pass the file-writing contract needed by the
researcher, engineer, backtester, or curator roles at this memory budget.

The installed Q4 models quantize **weights**. PolarQuant is a research method for
quantizing the **KV cache**, and is not an Ollama setting. Ollama supports `q8_0`
and `q4_0` KV cache types with Flash Attention, but the observed 1.9 GB loaded
size was already dominated by weights and runtime overhead at 4K context. Cache
compression would not make five concurrent local coding agents fit in 8 GB.
Keep contexts short and unload models after direct probes (`keep_alive: 0`).

Sources: [Ollama Qwen3 tags](https://ollama.com/library/qwen3/tags),
[Ollama cache FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx),
[PolarQuant paper](https://research.google/pubs/polarquant-quantizing-kv-caches-with-polar-transformation/).
