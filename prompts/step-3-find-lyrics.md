# Step 3: Find & Save Indic Language Lyrics

## Objective

Search for the original song lyrics in native Indic script (Telugu, Hindi, Tamil, etc.) using the video title, navigate to a lyrics website using Chrome DevTools MCP, extract the full lyrics, and save them to the workspace.

## Prerequisites

- `${WORKSPACE_DIR}/meta.json` exists with `video_title` and `language` fields
- Chrome DevTools MCP available

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

**See also:**
- [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation reference
- [Workspace Conventions > Native Script Rule](references/workspace-conventions.md#native-script-rule)

---

## Instructions

### 3.1 — Build the Search Query

Construct a Google search query using the video title from `meta.json`:

**Format:**
```
<song name> <language> lyrics
```

**Examples:**
- `Meesaala Pilla Telugu lyrics`
- `Oo Antava Telugu lyrics`
- `Malle Theegaroy Telugu lyrics`

Strip filler words from the video title for the search (e.g. "Full Lyrical", "Video Song", "Official", "HD", movie title, actor names).

---

### 3.2 — Try lyricstape.com First (Preferred for Telugu)

**Chrome DevTools MCP:** See [Common Navigation Patterns](references/chrome-devtools-patterns.md#common-navigation-patterns)

Navigate to:
```
https://www.lyricstape.com/?s=<url-encoded-song-name>
```

Take a snapshot to check if results appear. If a matching result is found, click it and skip to Step 3.4. If no results, fall back to Google search.

---

### 3.3 — Search Google for Lyrics (Fallback)

**Chrome DevTools MCP:**

Navigate to Google with the search query:
```
https://www.google.com/search?q=<url-encoded-search-query>
```

Try a site-scoped search for lyricstape.com first:
```
https://www.google.com/search?q=Meesaala+Pilla+Telugu+lyrics+site:lyricstape.com
```

Take a snapshot to see the search results.

---

### 3.4 — Identify the Best Lyrics Source from Google Results

If falling back to Google, scan the search results snapshot for links to Indic lyrics websites. Prefer sources that show native script in the snippet (not romanized/transliterated).

**Preferred sources (in priority order):**
1. lyricstape.com — Telugu lyrics in native Telugu script (top preferred source)
2. lyricsted.com — Telugu lyrics in Telugu script
3. lyricsmint.com — multilingual Indic lyrics
4. filmylyrics.com — Telugu/Hindi lyrics
5. lyricshindi.in — Hindi lyrics
6. lyricsintelugu.com — Telugu lyrics
7. Any site that shows Telugu/Devanagari/Tamil script in the search snippet

**Avoid:** Sites that only show romanized/transliterated lyrics

**See:** [Native Script Rule](references/workspace-conventions.md#native-script-rule) — Never use romanized text.

---

### 3.5 — Navigate to the Lyrics Page

**Chrome DevTools MCP:** Navigate to the best matching result URL.

Take a snapshot to verify the page loaded.

---

### 3.6 — Verify Lyrics Are in Native Script

After the page loads, confirm:
- Lyrics are displayed in native Indic script (e.g., Telugu: `మల్లె తీగరోయ్`)
- NOT in romanized form (e.g., "malle theegaroy" — skip this page)

If romanized only, go back and try the next result.

---

### 3.7 — Extract the Lyrics Text

**Chrome DevTools MCP:** Use `evaluate_script` with common selectors.

**See:** [Extract Text Content by Selector](references/chrome-devtools-patterns.md#extract-text-content-by-selector)

Review the extracted text to confirm it contains the correct Indic script lyrics.

---

### 3.8 — Save Lyrics to Workspace

**Write tool:** Save the extracted lyrics:

```
File path: ${WORKSPACE_DIR}/${SLUG}-lyrics.txt
```

Include a header with source metadata:

```
# Song: <video_title>
# Language: <language>
# Source: <lyrics page URL>
# Retrieved: <timestamp>

<full lyrics in native Indic script>
```

---

### 3.9 — Update meta.json Status

Update `${WORKSPACE_DIR}/meta.json` to mark this step complete:

```json
"status": {
  "mp3_downloaded": true,
  "acapella_extracted": true,
  "lyrics_saved": true,
  ...
}
```

Also add the lyrics source URL to `meta.json`:

```json
"lyrics_source_url": "<url of the lyrics page>"
```

---

### 3.10 — Confirm Lyrics Ready

Print a summary before proceeding:

```
Lyrics saved: <workspaceRoot>/<slug>/<slug>-lyrics.txt
Source: <lyrics URL>
Language: <language>
Lines: <count>

Proceeding to Step 4: Generate Suno Meta-Tag Lyrics...
```

---

## File Outputs

| File | Path |
|---|---|
| Raw lyrics (native script) | `<workspaceRoot>/<slug>/<slug>-lyrics.txt` |
| Updated metadata | `<workspaceRoot>/<slug>/meta.json` |

---

## Error Handling

**See**: [Error Handling Patterns > Lyrics Errors](references/error-handling-patterns.md#lyrics-errors-step-3) and [Browser Automation Errors](references/error-handling-patterns.md#browser-automation-errors-steps-3-5-7)

| Error | Solution |
|---|---|
| No Indic script lyrics found | Try queries with native language terms (e.g., `పాట సాహిత్యం` for Telugu) |
| Page requires JavaScript | Take screenshot to visually read lyrics |
| Partial lyrics found | Note missing sections in file header |
| Multiple scripts on page | Keep only Indic script section |

---

## Reference

- [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation
- [Workspace Conventions](references/workspace-conventions.md) — Native script rules
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
