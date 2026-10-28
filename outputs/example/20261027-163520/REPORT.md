# Rerun with official default prompts

October 27, 2026 | Illinois FPIF, 33-page PDF | INV-04 | Completed successfully.

Custom instructions and their command-line switch were removed from the runner. Both indexing and answering used the official implementation
and built-in prompts from pinned PageIndex 0.2.10.

## Configuration

| Setting | Value |
|---|---|
| Index model | gpt-6-luna, as in the official Quickstart |
| Chat model | gpt-6-sol, as in the official Quickstart |
| Reasoning effort in both stages | Explicitly medium, as requested |
| Index mode and optimization | Official defaults: Flash, full |
| Summary concurrency limit | Official default: 64 |
| Chat turn limit | Official default: 10 |
| Custom instructions | Not supplied; removed from the code |
| Optional citation prompt | Disabled, the official default |
| Timeouts, retries, output-token limits | No runner overrides; SDK defaults apply |

The officially supported Responses API was explicitly selected for tool use with medium reasoning.
The run reused the authorized connection configuration and created a fresh local index directory.
Models, reasoning effort, API protocol, connection, and storage were explicit runtime settings;
this does not claim that every parameter matches the shortest official Quickstart example.

## Answer and evidence

The question asks for FPIF's long-term private-market allocation and asset-class split. The model answered:

- Total private markets: **31%**.
- Private equity: **10%**.
- Private debt: **7%**.
- Real estate: **10%**.
- Infrastructure: **4%**.

The model called `get_document_structure`, then read pages 3-4 through `get_page_content`.
Its final answer cited Section 1.2, printed page 1 / PDF page 3 in ordinary text.
Both the answer and page reference matched the original source and scoring reference, which was consulted only after generation.

Because the optional citation prompt was disabled, there were no `<cite>` tags and `get_citations()` returned an empty list.
The answer still contained a correct textual source citation; see `result.json`.

## Timing and usage

| Stage | Time | Model responses | Input tokens | Output tokens |
|---|---:|---:|---:|---:|
| Indexing | 17.072 seconds | 17 | 22,809 | 4,418 |
| Retrieval and answering | 9.058 seconds | 3 | 15,253 | 175 |
| Total | 26.184 seconds | 20 | 38,062 | 4,593 |

Total usage was 42,655 tokens, with 912 reasoning tokens included in output tokens. Every request explicitly sent medium reasoning effort.
The chat responses reported zero reasoning tokens; this does not mean the request setting was absent.
Cached input tokens were 14,825 for indexing and 7,410 for answering.
Timing excludes dependency imports. This is a single observation; the latency change cannot be attributed to prompts alone.

## Verification

- All 17 indexing responses returned gpt-6-luna; all 3 chat responses returned gpt-6-sol, for 20 unique responses.
- All 20 actual HTTP requests used medium reasoning effort and the configured model.
- Every chat request's complete instructions exactly matched official `CHAT_HEADER + AGENT_INSTRUCTIONS`; the original text is saved.
- All 96 installed Python source files matched the pinned official source byte for byte.
- Official source commit: `e38b40ebaeea26d2c7206b80ce7bc9bf2935cdec`.
- Hashes were unchanged for all 82 core input files: PDFs, question data, and the manifest.
- Public-source verification and the same original page used in the earlier visual check are retained.

This remained a functional example with one specified document, not the full 110-question corpus evaluation.

## Records

- [Official instructions](official_chat_instructions.txt)
- [Full answer and run result](result.json)
- [Actual request parameters and prompt consistency](wire_requests.jsonl)
- [Tool-call trace](tool_trace.json)
- [Verification record](verification.json)
- [Runner snapshot](runner_snapshot.py)

![PDF page 3, printed page 1](evidence_page_3.png)
