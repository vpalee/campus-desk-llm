# Development history provenance

This project was built and committed locally in six actual stages during this session. The command-line GitHub credential was invalid, so the public repository was initialized and those existing development snapshots were imported sequentially through the connected GitHub API. These were not backdated commits. Public commit authors and timestamps describe the import; every imported file tree was checked against the corresponding original local Git tree.

The original commits are preserved locally on branch `local-development`. The published `main` branch contains the bootstrap commit, the six imported snapshots below, and this provenance note. The application and evaluation outputs were developed and tested before submission.

| Original local commit | Public import commit | Stage |
|---|---|---|
| `40656c391e5b284eb0cdbb0901da6e84063fd524` | [`b0ef601`](https://github.com/vpalee/campus-desk-llm/commit/b0ef601d5651b4556e0363233abba0ff944afb87) | Add fictional IT corpus and reproducible retrieval baseline |
| `7ee2a412da80142e8e79062d67c4ea77a8516204` | [`785b9a5`](https://github.com/vpalee/campus-desk-llm/commit/785b9a5277777f632bc8670008d879f8f2e62486) | Implement validated read-only class-proxy tool agent and API |
| `c293ac29491cca3f8e960b48fd0e746dd103a345` | [`8d1a22e`](https://github.com/vpalee/campus-desk-llm/commit/8d1a22e635d52678e6ad0c432f993a2696f0ebfa) | Add responsive answer-and-handbook interface with source navigation |
| `9376598833e16e62b14d8ca7ae59130230616e69` | [`a934775`](https://github.com/vpalee/campus-desk-llm/commit/a93477563a4001a1e34348473517d50c81d89bac) | Handle observed Gemma wire formats with strict parsing and boundary tests |
| `4b4717ffd98af90036336cca7e266158cadd8491` | [`7c7b1f9`](https://github.com/vpalee/campus-desk-llm/commit/7c7b1f9f22993e4d4df820c8f7ccb3f8c988c9c4) | Record live failures and add bounded JSON repair and query fallback |
| `c60b58f25ee03d69e52413129e75ea612bccd1e4` | [`5f876e9`](https://github.com/vpalee/campus-desk-llm/commit/5f876e9c6e6b85e598010f6b4246edcb5dc4fb4e) | Document measured trade-offs, real model evidence, setup, and demo handoff |
