# PaperLens

PaperLens is an evidence-grounded literature review assistant
designed to help students and researchers investigate questions
across collections of research papers.

Instead of generating answers from an LLM's general knowledge,
PaperLens retrieves relevant passages from the provided papers
and requires answers to reference their supporting evidence.

## Problem

Literature reviews require researchers to search across many papers,
compare findings, identify supporting or conflicting evidence, and
track which source supports each conclusion.

General-purpose language models can summarize papers, but generated
answers may combine claims from different sources or produce statements
that are not supported by the provided literature.

PaperLens explores whether retrieval-augmented generation can provide
useful research synthesis while keeping conclusions traceable to the
original evidence.

## Initial Research Domain

Retrieval-Augmented Generation and LLM hallucination.

## Planned Features

- Ask questions across multiple research papers
- Retrieve relevant passages
- Generate evidence-grounded answers
- Provide paper and page-level citations
- Compare findings across papers
- Identify supporting and conflicting evidence
- Check whether a claim is supported by the corpus
- Abstain when sufficient evidence cannot be found

## Evaluation

PaperLens will be evaluated using a manually labeled set of research
questions with known relevant source papers/passages.

Initial metrics:

- Recall@5
- Citation support rate
- Answer correctness
- Response latency

## Status

🚧 Research prototype under active development.