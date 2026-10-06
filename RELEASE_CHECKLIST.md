# Release Checklist

## Validation

- [ ] Missing required Excel column stops the batch
- [ ] Missing candidate field skips only that candidate
- [ ] Invalid email skips only that candidate
- [ ] Invalid `tone` skips only that candidate
- [ ] Invalid experience value skips only that candidate
- [ ] Invalid `client_id` skips only that candidate
- [ ] Duplicate `client_id` is detected
- [ ] Duplicate record is skipped
- [ ] Processing continues after skipped records

## Generation

- [ ] Valid candidate generates `resume.docx`
- [ ] Valid candidate generates `cover_letter.docx`
- [ ] One generation failure does not stop the batch
- [ ] Generation failure is counted as `failed`
- [ ] Invalid input record is counted as `skipped`

## Batch Report

- [ ] `batch_report.json` is created
- [ ] `processed` count is correct
- [ ] `succeeded` count is correct
- [ ] `skipped` count is correct
- [ ] `failed` count is correct
- [ ] skipped records contain `client_id`
- [ ] skipped records contain Excel row number
- [ ] skipped records contain error description
- [ ] failed records contain `client_id`
- [ ] failed records contain error description

## Documents

Open at least one generated resume and cover letter.

Verify:

- [ ] candidate name is correct
- [ ] email is correct
- [ ] location is correct
- [ ] target role is correct
- [ ] skills match Excel data
- [ ] key achievement matches Excel data
- [ ] professional summary contains no obvious invented facts
- [ ] resume formatting is readable
- [ ] cover-letter formatting is readable
- [ ] placeholders are fully replaced

## GUI

- [ ] GUI starts correctly
- [ ] Excel browse button works
- [ ] output-folder browse button works
- [ ] Generate Documents button works
- [ ] progress indicator appears during processing
- [ ] GUI remains responsive during generation
- [ ] completion popup appears
- [ ] warning popup appears when records are skipped or failed
- [ ] application icon appears in Explorer
- [ ] application icon appears in the window
- [ ] application icon appears on the Windows taskbar

## AI Bootstrap

- [ ] existing Ollama installation is detected
- [ ] existing `qwen2.5:3b` model is detected
- [ ] application can generate documents through Ollama
- [ ] useful error is displayed if AI setup fails

## Tests

Run:

```powershell
python -m pytest -q
```

Required result:

```text
all tests passed
```

## Build

Run:

```powershell
.\build.ps1
```

Expected output:

```text
dist/
└── BatchAIDocumentGenerator/
    ├── BatchAIDocumentGenerator.exe
    └── _internal/
```

## Final Smoke Test

Prepare an Excel file containing:

```text
C001 -> valid
C002 -> missing required value
C003 -> valid
C001 -> duplicate ID
C004 -> valid
```

Verify that:

```text
C001 first record -> generated
C002              -> skipped
C003              -> generated
C001 duplicate    -> skipped
C004              -> generated
```

Verify that `batch_report.json` reports:

```text
processed = 5
succeeded = 3
skipped   = 2
failed    = 0
```

Then test a separate Excel file with an entire required column removed.

Verify:

```text
batch stops
no candidates are generated
validation popup is displayed
```

## Git Status

Run:

```powershell
git status
```

The following should not be committed:

```text
build/
dist/
*.spec
output/
.env
.env.*
```

## Final Commit

Run:

```powershell
git add .
git status
git commit -m "Complete Batch AI Document Generator"
git push
```

## Optional Tag

After the final commit is pushed:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

## Distribution

Distribute the complete directory:

```text
dist\BatchAIDocumentGenerator\
```

Do not distribute only:

```text
BatchAIDocumentGenerator.exe
```

because the current PyInstaller build uses `onedir` mode.