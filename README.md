# Live SWE-Agent Leaderboard

A leaderboard website for tracking the performance of language models using the Live-SWE-agent scaffold on SWE-bench Verified and SWE-Bench Pro datasets.

## Editing Page Content

To customize the About page, edit the Markdown file in the `content/` directory:

```bash
content/
└── about.md        # Edit the About section
```

This file supports standard Markdown syntax including headings, lists, links, code blocks, tables, and text formatting.

After editing, rebuild the site:

```bash
make build
```

## Adding New Models

To add new models to existing leaderboards, edit `data/leaderboards.yaml` and add entries under the `results` section:

```yaml
results:
  - model: "Model Name"
    org: "Organization"
    resolved: 65.5        # Percentage resolved (0-100)
    avg_cost: 0.45        # Average cost per instance ($)
    date: "2025-01-15"    # Submission date (YYYY-MM-DD)
    open_source: true     # true for open source, false for proprietary
    verified: true        # true if verified by our team
    tags:
      - "Org: Organization Name"
      - "Type: Open Source"  # or "Type: Proprietary"
```

## Adding New Benchmarks

To add a new benchmark tab, add a new leaderboard entry in `data/leaderboards.yaml`:

```yaml
leaderboards:
  - display_name: Your Benchmark Name
    info_sections:
      - title: Benchmark Title
        content: Description of the benchmark.
    results:
      - model: "Model Name"
        org: "Organization"
        resolved: 50.0
        avg_cost: 0.30
        date: "2025-01-15"
        open_source: false
        verified: true
        tags:
          - "Org: Organization"
          - "Type: Proprietary"
```

After updating the YAML file, rebuild:

```bash
make build
```

## Acknowledgement

Inspired by the [SWE-bench](https://swebench.com) leaderboard design.