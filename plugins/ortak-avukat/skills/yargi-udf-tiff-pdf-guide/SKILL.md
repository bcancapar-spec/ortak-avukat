---
name: yargi-udf-tiff-pdf-guide
description: Use when reading or writing UYAP case-file formats (.udf, .tiff, .pdf) (version 2026-06-22)
---

# UYAP Document Format Guide (UDF · TIFF · PDF)

Guide version: 2026-06-22

This guide teaches you, an autonomous AI agent, how to read (and for UDF, write) the three document formats you meet in UYAP (Turkey's Ulusal Yargı Ağı / National Judiciary Informatics System) case files: **UDF**, **multi-page TIFF**, and **PDF**. Each format has a pitfall that silently loses content if you read it naively — this guide tells you how to avoid each one. Prefer zero-install `npx` tools; fall back to OS-native tools only where no good `npx` option exists.

## Which format → which tool

| You have | The trap | Do this |
|---|---|---|
| `.udf` | Opaque UYAP format — raw read shows binary; never hand-edit | `npx -y udf-cli@latest udf2md file.udf` (Section A) |
| `.tiff` / `.tif` | Multi-page TIFF shows only the FIRST page when read raw | `npx -y uyap-tiff-cli@latest tiff2pdf file.tiff` → read the PDF (Section B) |
| `.pdf` | Scanned (image-only) PDFs have no embedded text | `npx -y uyap-pdf-cli@latest pdf2md file.pdf` — text first, auto-OCR fallback (Section C) |

A `.udf` that is actually a mislabelled PDF/DOCX (wrong extension) will fail `udf2md` — when that happens, treat it by its real type. Going the other way — need to *produce* a `.udf` from an existing `.docx` or `.pdf`? See `docx2udf` in Section A.5.

## Authentication (login once, then every command works)

`udf-cli`, `uyap-tiff-cli` and `uyap-pdf-cli` are **login-gated** — they verify the user's account (login / ban / quota) on each run and need network access. The token is stored at `~/.config/yargi/token.json`, auto-refreshes, and is **shared across all three CLIs**, so you log in once. Pick the path that matches your environment:

*   **Interactive (a human is present with a browser):** run `npx -y udf-cli@latest login` once. It prints a verification URL + code and **blocks until the human approves in a browser**. Relay the URL and code to the user if it can't open one itself.
*   **Non-interactive / headless (you are an automated agent in a sandbox, no browser):** the browser login above will hang forever. Instead, **call the `issue_cli_login_code` MCP tool** — it returns a single-use code (valid ~2 min). Then run `udf-cli login --token <code>` (or `uyap-tiff-cli` / `uyap-pdf-cli`). That establishes a **self-refreshing session**, so you do NOT request a new code per command — only re-call `issue_cli_login_code` if a CLI reports the session expired. (This non-interactive path does not exist for `dava-cli`, which needs a real browser for UYAP.)

If a command exits asking for auth, you are not logged in — run the matching login path above, then retry. Check status with `<cli> whoami`; clear the shared token with `<cli> logout`.

## A. UDF — Reading and Writing

A UDF is an opaque UYAP format that only `udf-cli` can read or produce. Do NOT assume its internals, and never hand-write or hand-edit a `.udf` — always go through the `udf-cli` npm package, which handles the format for you. Zero-install via `npx -y` (no global install needed).

### A.1 Reading a UDF (`udf2md` / `udf2html`)

```bash
# Read a UDF as Markdown straight to stdout (agent-friendly — just read the output)
npx -y udf-cli@latest udf2md "evraklar/Gelen/02-Dilekceler/2026-03-12_Cevap_Dilekcesi.udf"

# For complex formatting inspection, get HTML instead
npx -y udf-cli@latest udf2html input.udf
```

Tables become Markdown tables; bold/italic use `**`/`*`; lists become `1.`/`-`.

Reading rules:
1. Do NOT write the raw `.udf` to disk as `.md`/`.html` — just read the converted content.
2. To read many documents, follow INDEX.md order and call `udf2md` once per file.
3. If `udf2md` errors, the file may not be a real UDF (a PDF/DOCX given the wrong extension) — handle it by its actual type.
4. To *edit* a UDF in a native GUI editor (not just read it), the user can install the UYAP Doküman Editörü on macOS Apple Silicon — call the `install_additional_tools` tool for instructions.

### A.2 Writing a UDF (always `html2udf`)

> **Always write UDF with `html2udf`. Never use `md2udf`.** HTML gives you full control over fonts, inline styles, paragraph spacing, indentation, tab stops, tables, and colors — the things UYAP documents need. Markdown supports only a small subset and silently drops everything else, so `md2udf` is not an acceptable path even for quick drafts. Author inline-CSS HTML and convert it with `html2udf`, every time.

> `html2udf` is for **authoring** a UDF from content you produce. If you instead already have a finished `.docx` or `.pdf` file and just need it as `.udf` (e.g. the user drafted a dilekçe in Word), use the login-gated `docx2udf` tool — see Section A.5.

```bash
# Author inline-CSS HTML, convert to UDF
npx -y udf-cli@latest html2udf taslak.html cikti.udf

# Input also accepts a raw string or '-' for stdin
echo '<p><strong>Merhaba</strong> dünya</p>' | npx -y udf-cli@latest html2udf - cikti.udf
```

### A.3 AI authoring rules for UDF-compatible HTML

When generating UDF input, produce **HTML with inline CSS** and convert with `html2udf`. Use `pt` for all lengths.

> - **Default:** when no `font-family` / `font-size` is set, text is **Times New Roman 12pt**, black on white. Omit these unless a different style is requested.
> - **Inline styles:** `<strong>`, `<em>`, `<u>`, `<span style="font-family:Arial; font-size:12pt; color:#FF0000; background-color:#FFFF00">`
> - **Paragraphs:** `<p style="text-align:justify; line-height:1.5; margin-top:12pt; margin-bottom:6pt; margin-left:36pt; text-indent:24pt">` (also `text-align:right`, hanging indent via negative `text-indent`)
> - **Headings:** `<h1>`–`<h6>` produce bold paragraphs at 24/20/16/14/12/10pt
> - **Tab stops:** `<p style="tab-stops:36pt 72pt 108pt">Item<tab/>Value<tab/>Notes</p>`
> - **Page break:** `<page-break/>` — **only when the user explicitly asks for one**. The UDF editor renders a visible "sayfa sonudur" marker readers often mistake for content. Default to natural page flow.
> - **Tables:** standard `<table><tr><td>...</td></tr></table>`; supports `colspan`/`rowspan`; cell styles via inline CSS (`background-color`, `vertical-align`, `border`, `border-style:none` to hide borders)
> - **Lists:** `<ul>`, `<ol>`, `<li>` (nest via nested lists)
> - **Images:** `<img src="data:image/png;base64,..." width="200" height="100">` (width/height in `pt`)
> - **Colors:** hex (`#RGB`, `#RRGGBB`), `rgb(r,g,b)`, or named CSS colors all work
>
> Always use `pt`. Do not escape `<tab/>` or `<page-break/>`. Do not use `<br>` to separate paragraphs — start a new `<p>`.

Unit rules: always use `pt`. Bare numbers (`margin-top:12`) are treated as `pt`. Conversion exists for `px`/`em`/`rem`/`cm`/`mm`/`in` but don't rely on it.

Common mistakes:

| Wrong | Right | Why |
|---|---|---|
| `font-size:14px` | `font-size:14pt` | UDF uses points |
| `&lt;tab/&gt;` | `<tab/>` | Escaped custom elements become literal text |
| `<br><br>` for paragraph break | Two separate `<p>` blocks | UDF is block-based; `<br>` is intra-paragraph soft break |
| `<div>` for inline text | `<p>` for paragraph text | `<div>` is a block group, `<p>` is a paragraph |

### A.4 UDF cookbook

Coloured bold heading:
```html
<p style="text-align:center"><span style="font-family:Arial; font-size:18pt; color:#003366"><strong>BAŞLIK</strong></span></p>
```

Justified paragraph with first-line indent:
```html
<p style="text-align:justify; text-indent:24pt; line-height:1.5">Lorem ipsum dolor sit amet ...</p>
```

Three-column tab-stop layout (signature block):
```html
<p style="tab-stops:200pt 400pt"><strong>Davacı</strong><tab/><strong>Davalı</strong><tab/><strong>Hâkim</strong></p>
<p style="tab-stops:200pt 400pt">Mehmet Yılmaz<tab/>Ahmet Demir<tab/>Ayşe Kaya</p>
```

Yellow-highlighted span:
```html
<p>Bu cümlede <span style="background-color:#FFFF00">vurgulanmış kısım</span> var.</p>
```

Bordered table with bold header row:
```html
<table>
  <tr>
    <td style="background-color:#EEEEEE"><strong>Sıra</strong></td>
    <td style="background-color:#EEEEEE"><strong>Açıklama</strong></td>
  </tr>
  <tr>
    <td>1</td>
    <td>Birinci kalem</td>
  </tr>
</table>
```

Numbered list with a nested bullet list:
```html
<ol>
  <li>Birinci madde</li>
  <li>İkinci madde
    <ul>
      <li>Alt madde a</li>
      <li>Alt madde b</li>
    </ul>
  </li>
  <li>Üçüncü madde</li>
</ol>
```

Hanging indent (negative `text-indent`):
```html
<p style="margin-left:36pt; text-indent:-36pt">DAVACI<tab/>: [AD SOYAD], T.C. Kimlik No [TCKN], [IL]</p>
```

Table with merged cells (`colspan` / `rowspan`):
```html
<table>
  <tr>
    <td rowspan="2" style="vertical-align:middle"><strong>Kalem</strong></td>
    <td colspan="2" style="text-align:center"><strong>Tutar</strong></td>
  </tr>
  <tr>
    <td>Net</td>
    <td>KDV Dahil</td>
  </tr>
  <tr>
    <td>Vekalet ücreti</td>
    <td>1.000 TL</td>
    <td>1.200 TL</td>
  </tr>
</table>
```

Borderless table (layout grid, no visible lines):
```html
<table>
  <tr>
    <td style="border-style:none">Sol sütun</td>
    <td style="border-style:none">Sağ sütun</td>
  </tr>
</table>
```

### A.5 Converting an existing DOCX or PDF into UDF (`docx2udf`)

When you already have a finished **`.docx` or `.pdf`** file and just need it as **`.udf`** — rather than authoring content yourself with `html2udf` — use the **`docx2udf`** npm package. Zero-install via `npx -y`. Unlike `udf-cli`, it is **login-gated**: it checks the user's account (login/ban/quota) before converting, and **fails closed** if the server is unreachable.

```bash
# DOCX → UDF
npx -y docx2udf@latest -input dilekce.docx -output dilekce.udf

# PDF → UDF (-output optional; defaults to the input path with a .udf extension)
npx -y docx2udf@latest -input /tmp/karar.pdf
```

Rules:
1. Always pass `-y` so `npx` never blocks on its interactive `Ok to proceed?` prompt.
2. `-input` accepts `.docx` or `.pdf` (extension is case-insensitive).
3. Judge success by the **exit code plus the presence of the `-output` file** — do NOT parse stdout/stderr text.
4. Discover commands/options/exit codes live with `npx -y docx2udf@latest --help`.

> **Page-break markers in the output.** To match the source Word document page-for-page, the produced UDF inserts `---Sayfa Sonu---` lines at each page break. **These are NOT real document text — they are only page-cut markers.** When summarising or quoting the converted UDF, ignore them. The user can delete each `---Sayfa Sonu---` line by hand in the UDF editor and re-flow the text with Enter if they prefer natural page flow.

Exit codes — what to do:

| Code | Meaning | Action |
|---|---|---|
| 0 | Success | Use the `-output` file |
| 1 | Conversion/input error (unsupported format, file missing, unexpected server response) | Read stderr; fix the input or report it |
| 2 | Login required | Run the login flow below, then retry the conversion |
| 3 | Account banned | Stop; tell the user |
| 4 | Server unreachable (network / 5xx) | Transient — retry later |
| 5 | Monthly quota exhausted | Tell the user; wait for next month or upgrade |

**Login flow (you trigger it; a human approves in the browser):**

```bash
npx -y docx2udf@latest login
```

This prints a verification URL and a user code to stderr, e.g. `https://....authkit.app/device?user_code=XXXX-YYYY`, and **blocks until the human approves**. It tries to open the browser itself; if it can't (headless), relay the URL **and** the code to the user, then wait for the command to finish before retrying the conversion. Login is needed once — the token is stored at `~/.config/yargi/token.json`, auto-refreshes, and is **shared with the other "yargi" CLIs (`udf-cli`, `dava-cli`)**, so if the user already logged in through one of those, `docx2udf` is already authenticated. Check status with `npx -y docx2udf@latest whoami`; clear the shared token with `npx -y docx2udf@latest logout`.

## B. TIFF — Reading multi-page scans

A multi-page TIFF is a single container holding many page images. **If you read it raw, only the FIRST page is visible** — so a 5-page tebligat mazbatası silently becomes 1 page. This matters most for tebligat mazbataları (notification receipts): the tebellüğ (service) date can be on the first OR last page, so missing pages means missing the date.

### B.1 Preferred — `uyap-tiff-cli` (zero-install, any OS)

```bash
# Convert ALL pages into a single PDF, then read that PDF natively (Section C)
npx -y uyap-tiff-cli@latest tiff2pdf dosya.tiff          # → dosya.pdf, prints the page count

# Runtime cannot ingest PDFs/images at all? OCR straight to Markdown instead
npx -y uyap-tiff-cli@latest tiff2md dosya.tiff           # local Turkish OCR → Markdown on stdout
```

> **Login required.** As of v0.2.0 this tool needs a one-time `npx -y uyap-tiff-cli@latest login` (WorkOS device flow; the same login as `dava-cli`, stored in `~/.config/yargi/token.json`). Without it, conversions fail with a Turkish "önce giriş yapın" message and exit 1. It also needs network access on every run (usage is reported to the server) — it no longer works fully offline.

Rules:
1. `tiff2pdf` is the default path — one command, every page preserved in order, no scratch PNGs to clean up. Read the produced PDF like any PDF (Section C).
2. Judge success by the exit code plus the output file existing; errors are Turkish on stderr. Do not parse stdout beyond the page count line.
3. `tiff2md` runs LOCAL OCR (tesseract, `tur` model — downloaded to `~/.cache/uyap-tiff-cli/` on first run). Good on clean scans, weaker on noisy faxes — prefer reading the `tiff2pdf` output visually when your runtime can.
4. In `tiff2md` output, `## Sayfa N` headings are page markers, NOT document content.

### B.2 Fallback — OS-native tools (only when npx is unavailable)

ImageMagick (any OS): `magick identify dosya.tiff` to count pages, then `magick dosya.tiff sayfa-%02d.png` to split (older installs use `convert`). macOS built-in: `tiffutil -info dosya.tiff`, `tiffutil -extract N dosya.tiff -out sayfaN.tiff`, then `sips -s format png sayfaN.tiff --out sayfaN.png`. Windows built-in PowerShell:

```powershell
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile("dosya.tiff")
$fd  = New-Object System.Drawing.Imaging.FrameDimension $img.FrameDimensionsList[0]
for ($i = 0; $i -lt $img.GetFrameCount($fd); $i++) {
  $img.SelectActiveFrame($fd, $i); $img.Save("sayfa-$i.png", [System.Drawing.Imaging.ImageFormat]::Png)
}
$img.Dispose()
```

Read ALL generated pages **in order** and delete the temporary files when done.

## C. PDF — Reading

**First, convert the PDF with `uyap-pdf-cli` (zero-install, one command).** It extracts the embedded text with `@opendocsg/pdf2md` and AUTOMATICALLY falls back to local Turkish OCR (tesseract.js) when the PDF is scanned — so one command handles both text and image-only PDFs:

```bash
npx -y uyap-pdf-cli@latest pdf2md dosya.pdf            # → Markdown on stdout (or: pdf2md dosya.pdf cikti.md)
```

`pdf2md` is login-gated (shares your UYAP login) — run `npx -y uyap-pdf-cli@latest login` once if it exits asking for auth. The `tur` OCR model downloads to `~/.cache/uyap-pdf-cli/` on the first scanned PDF.

### C.1 Fallback — read the PDF natively

If `npx` is unavailable (or you just want to spot-check one document), read the `.pdf` directly via your file/Read tool. Modern multimodal agents (Claude, Gemini, GPT-4o-class) read `.pdf` files directly — that handles both text and scanned pages.

### C.2 Fallback — manual extraction (no uyap-pdf-cli, can't read natively)

Extract embedded text with `@opendocsg/pdf2md`, which only works on a FOLDER:

```bash
IN=$(mktemp -d); OUT=$(mktemp -d)
cp "evraklar/Gelen/01-Mahkeme_Kararlari/2026-04-01_Karar.pdf" "$IN/"
npx -y @opendocsg/pdf2md@latest --inputFolderPath="$IN" --outputFolderPath="$OUT"
# Read $OUT/2026-04-01_Karar.md, then: rm -rf "$IN" "$OUT"
```

An empty result means the PDF is **scanned (image-only)** — rasterise and read the pages visually: ImageMagick (needs Ghostscript) `magick -density 200 dosya.pdf sayfa-%02d.png`, then read every PNG in order, or OCR them with the system `tesseract` binary (`tesseract sayfa-01.png cikti -l tur`).

PDF rules:
- `uyap-pdf-cli pdf2md` first (text + auto-OCR); native read or manual extraction only as fallback.
- Read ALL pages in order; delete scratch files and folders when done.

## D. Final pitfalls reminder

1. **UDF is an opaque UYAP format — only `udf-cli` produces it.** Never read `.udf` raw and never hand-write/hand-edit one — always go through `npx -y udf-cli@latest`. Don't write the raw file to disk as `.md`/`.html`; read the converted content.
2. **Multi-page TIFF hides every page but the first.** Never read a `.tiff` raw — run `npx -y uyap-tiff-cli@latest tiff2pdf` and read the produced PDF (all pages, in order). The tebellüğ date may be on the last page.
3. **Scanned PDFs have no text.** `uyap-pdf-cli pdf2md` extracts text and auto-OCRs scanned PDFs in one command; if you fall back to manual extraction and get nothing, the PDF is scanned — rasterise to images and read visually.
4. **When writing UDF:** always use `pt`; never escape `<tab/>` or `<page-break/>`; `<p>` for paragraphs (not `<br>`); page breaks only when explicitly requested. Always use `html2udf`; never use `md2udf`. To convert an *existing* `.docx`/`.pdf` to UDF, use the login-gated `docx2udf` (Section A.5) — judge it by exit code, and handle exit 2 by running `docx2udf login`.
5. **Clean up scratch files** (split pages, temp folders) so you don't pollute `evraklar/` or `cikti/`.
