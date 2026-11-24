# SmartCommit

A lightweight CLI tool that writes Conventional Commit messages for you using your local Ollama models. No API keys, no cloud tracking, and zero external Python dependencies.

## Why?
Writing good commit messages gets tedious, and paying for API tokens just to summarize a `git diff` feels unnecessary when local models run fast enough on your own machine. This runs completely offline using standard Python and whatever models you already have in Ollama.

## What it does
- Stages your changes (`git add .`) and reads the diff.
- Generates a clean, single-line Conventional Commit message (`feat:`, `fix:`, `refactor:`, etc.).
- Opens an interactive prompt so you can:
  - **`y`** — commit right away
  - **`e`** — edit the message in your default editor before committing
  - **`r`** — regenerate a new suggestion
  - **`m`** — switch to a different local Ollama model
  - **Type anything else** — tell the model how to tweak the message (e.g., *"make it shorter"* or *"mention the config fix"*)
- Optionally pushes to your remote branch right after committing.

## Setup

You'll need **Python 3.8+** and **[Ollama](https://ollama.com)** running locally with at least one model pulled (defaults to `gemma4:e4b`):

```bash
ollama pull gemma4:e4b