# Corpus provenance

The 16 short articles in `articles.json` are an original, fictional university IT handbook authored with AI assistance for this capstone on 2026-10-27. They are not KMITL policies or advice about a real institution. No student data, private documents, or scraped university text is included. Each article is one retrieval unit; there is no overlap or hidden external corpus. The author releases these demo documents under the repository MIT license.

The glossary was authored with the corpus, before running the test comparison. It encodes illustrative English helpdesk vocabulary. It is not a learned embedding model, and English-only coverage is a limitation.

Evaluation questions and relevance labels are AI-assisted, author-curated synthetic examples, not independently hand-labelled or collected from real users. `dev.jsonl` has 10 development cases. `test.jsonl` has 30 separate cases (26 answerable, 4 out of scope). The split is by question, not topic; every supported topic appears in the corpus. Out-of-scope cases with overlapping vocabulary intentionally probe false matches. Retrieval labels do not assess answer quality or safe refusal of actions; see live evaluation for model behavior. Do not tune on the test set after reporting results.
