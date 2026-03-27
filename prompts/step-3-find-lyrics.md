# Step 3: Find & Save Indic Language Lyrics

## Objective

Search for the original song lyrics in native Indic script (Telugu, Hindi, Tamil, etc.) using the video title, navigate to a lyrics website using Chrome DevTools MCP, extract the full lyrics, and save them to the workspace.

## Prerequisites

- `workspaces/<slug>/meta.json` exists with `video_title` and `language` fields
- The song is a Telugu or other Indic language song

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

**Chrome DevTools MCP tool:** `navigate_page`

For Telugu songs, first attempt a direct search on lyricstape.com before falling back to Google:

```
URL: https://www.lyricstape.com/?s=<url-encoded-song-name>
```

Example:
```
URL: https://www.lyricstape.com/?s=Meesaala+Pilla
```

Take a snapshot to check if results appear:
```
Tool: take_snapshot
```

If a matching result is found, click it and skip to Step 3.4. If no results, fall back to the Google search in the next step.

---

### 3.3 — Search Google for Lyrics (Fallback)

**Chrome DevTools MCP tool:** `navigate_page`

If lyricstape.com did not return results, navigate to Google with the search query:

```
URL: https://www.google.com/search?q=<url-encoded-search-query>
```

Example:
```
URL: https://www.google.com/search?q=Meesaala+Pilla+Telugu+lyrics+site:lyricstape.com
```

Try a site-scoped search for lyricstape.com first, then broaden if needed:
```
URL: https://www.google.com/search?q=Meesaala+Pilla+Telugu+lyrics
```

Take a snapshot to see the search results:
```
Tool: take_snapshot
```

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

**Avoid:** Sites that only show romanized/transliterated lyrics (e.g., "malle theegaroy" instead of "మల్లె తీగరోయ్")

**Chrome DevTools MCP tool:** `take_snapshot`

Read the search result snippets to identify which site has native script lyrics.

---

### 3.5 — Navigate to the Lyrics Page

**Chrome DevTools MCP tool:** `navigate_page`

Click on the best matching lyrics result or navigate to its URL directly.

```
Tool: navigate_page
Type: url
URL: <lyrics page URL from search results>
```

Take a snapshot to verify the page loaded:
```
Tool: take_snapshot
```

---

### 3.6 — Verify Lyrics Are in Native Script

After the page loads, take a snapshot and confirm:
- Lyrics are displayed in native Indic script (e.g., Telugu: మల్లె తీగరోయ్)
- NOT in romanized form (e.g., "malle theegaroy" is romanized — skip this page)

If the page shows romanized lyrics only, go back and try the next result:
```
Tool: navigate_page
Type: back
```

---

### 3.7 — Extract the Lyrics Text

**Chrome DevTools MCP tool:** `evaluate_script`

Once on a valid lyrics page with native script, extract the full lyrics text using JavaScript:

```javascript
() => {
  // Try common lyrics container selectors
  const selectors = [
    '.lyrics', '.lyric', '.song-lyrics', '.lyrics-body',
    '[class*="lyric"]', '[class*="Lyric"]',
    'article', '.entry-content', '.post-content', 'main p'
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el && el.innerText.trim().length > 100) {
      return el.innerText.trim();
    }
  }
  // Fallback: get all paragraph text
  return Array.from(document.querySelectorAll('p'))
    .map(p => p.innerText.trim())
    .filter(t => t.length > 20)
    .join('\n\n');
}
```

Review the extracted text to confirm it contains the correct Indic script lyrics.

---

### 3.8 — Save Lyrics to Workspace

**Write tool** (filesystem, not browser):

Save the extracted lyrics to the workspace:

```
File path: workspaces/<slug>/<slug>-lyrics.txt
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

Update `workspaces/<slug>/meta.json` to mark this step complete:

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
Lyrics saved: workspaces/<slug>/<slug>-lyrics.txt
Source: <lyrics URL>
Language: <language>
Lines: <count>

Proceeding to Step 4: Generate Suno Meta-Tag Lyrics...
```

---

## File Outputs

| File | Path |
|---|---|
| Raw lyrics (native script) | `workspaces/<slug>/<slug>-lyrics.txt` |
| Updated metadata | `workspaces/<slug>/meta.json` |

---

## Error Handling

- **No Indic script lyrics found in search results:** Try alternative queries:
  - `<song name> <language> పాట సాహిత్యం` (for Telugu, adds "song lyrics" in Telugu)
  - `<song name> lyrics <movie name>`
  - Search YouTube comments for lyrics if no dedicated site found
- **Lyrics page requires JavaScript and won't load properly:** Try taking a screenshot instead to visually read the lyrics, then manually transcribe into the file.
- **Partial lyrics found:** Note which sections are missing in a comment at the top of `<slug>-lyrics.txt` so Step 4 can handle gaps appropriately.
- **Lyrics in multiple scripts on same page:** Only keep the Indic script section — remove any romanized or English translation sections before saving.

