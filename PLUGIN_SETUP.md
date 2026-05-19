# Plugins: you do not need Sonatype / Browse / Aikido MCP

Cursor MCP plugins are **optional**. This repo includes **built-in replacements** — run one command:

```powershell
cd e:\Amit\MarutiSuzuki
.\tasks.ps1 plugin-check
```

Or step by step:

| Broken MCP | Replacement in this repo |
|------------|---------------------------|
| **Sonatype** | `.\tasks.ps1 pins` + `.\tasks.ps1 audit` |
| **Aikido** | Same as Sonatype — `.\tasks.ps1 audit` |
| **Browse** | `.\tasks.ps1 test-e2e` (Playwright clicks **Run analysis**) |

## Browse MCP auto-repair

If you still want the Browse **Cursor plugin**, we can install its CLI binary without your login:

```powershell
.\tasks.ps1 fix-browse
```

Then **restart Cursor** once (MCP only picks up `browse.cmd` after reload).

## Optional env (not plugins)

- `FRED_API_KEY` in `.env` — better commodity data
- Hugging Face MCP — optional; app uses keyword rules by default

## Last MCP probe (Cursor-side, may differ after fix-browse + restart)

| Plugin | Typical status |
|--------|----------------|
| Context7 | Working |
| Hugging Face | Working |
| Neon | Working |
| Sonatype | Needs Sonatype account in Cursor |
| Browse | Fixed by `.\tasks.ps1 fix-browse` + Cursor restart |
| Aikido | Needs Aikido account in Cursor |

Your **website does not use any of these at runtime.**
