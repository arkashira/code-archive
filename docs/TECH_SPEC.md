# TECH_SPEC.md – Code Archive CLI

---

## 1. Overview

**Code Archive** is a lightweight command‑line interface (CLI) that creates deterministic snapshots of Git repositories.  
Snapshots are stored as compressed archives (`.tar.gz`) containing the repository’s file tree at a specific commit or tag, along with metadata (commit hash, author, date, etc.). The tool is designed for:

- **Backup & restore** of source code at known states.
- **CI/CD artifact generation** for reproducible builds.
- **Archival** of open‑source projects for research or compliance.

The CLI is written in **Go** (v1.22+), compiled to a single binary, and has no external runtime dependencies.

---

## 2. Architecture

```
┌───────────────────────┐
│  User (CLI Invocation)│
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  cmd/code-archive     │
│  (entry point, flags) │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  internal/cli         │
│  (flag parsing, help) │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  internal/archive     │
│  (core snapshot logic)│
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  internal/git         │
│  (git plumbing)       │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────┐
│  external deps         │
│  - go-git (git plumbing)│
│  - tar, gzip (std lib) │
└───────────────────────┘
```

### 2.1 Core Flow

1. **Parse CLI arguments** – repository path or URL, commit/branch/tag, output directory, optional filters.
2. **Validate repository** – ensure it is a valid Git repo or clone it temporarily.
3. **Checkout target commit** – using `go-git` to read the tree at the specified reference.
4. **Walk tree** – recursively collect file entries, preserving permissions and symlinks.
5. **Create archive** – stream files into a `tar.gz` writer, adding a `metadata.json` file with snapshot info.
6. **Persist output** – write the archive to the specified location, optionally compute SHA‑256 checksum.

---

## 3. Components

| Package | Responsibility | Key Types / Functions |
|---------|----------------|-----------------------|
| `cmd/code-archive` | CLI bootstrap | `main()` |
| `internal/cli` | Flag parsing, help text | `ParseFlags()`, `PrintHelp()` |
| `internal/archive` | Snapshot orchestration | `CreateSnapshot(ctx, cfg) error` |
| `internal/git` | Git plumbing | `OpenRepository(path string) (*git.Repository, error)`<br>`GetTree(repo *git.Repository, ref string) (*object.Tree, error)` |
| `internal/archive/archiver` | Tar/Gzip streaming | `NewTarGzipWriter(w io.Writer) *tar.Writer`<br>`AddFile(tw *tar.Writer, path string, content []byte, mode os.FileMode)` |
| `internal/archive/metadata` | Snapshot metadata | `Metadata{Commit, Author, Date, Ref, Size, Checksum}` |

---

## 4. Data Model

```go
type Metadata struct {
    // Commit hash (SHA-1)
    Commit string `json:"commit"`
    // Branch/Tag/Ref used
    Ref    string `json:"ref"`
    // Commit author name
    Author string `json:"author"`
    // Commit author email
    Email  string `json:"email"`
    // Commit date (RFC3339)
    Date   string `json:"date"`
    // Size of the archive in bytes
    Size   int64  `json:"size"`
    // SHA-256 checksum of the archive
    Checksum string `json:"checksum"`
}
```

The `metadata.json` file is added as the first entry in the tarball.

---

## 5. Key APIs / Interfaces

| API | Description | Example |
|-----|-------------|---------|
| `CreateSnapshot(ctx context.Context, cfg SnapshotConfig) (string, error)` | Main entry point. Returns path to created archive. | `CreateSnapshot(ctx, SnapshotConfig{Repo:"https://github.com/owner/repo.git", Ref:"v1.2.3", OutDir:"./snapshots"})` |
| `SnapshotConfig` | Configuration struct for snapshot creation. | `type SnapshotConfig struct { Repo string; Ref string; OutDir string; Filter func(path string) bool }` |
| `Filter` | Optional function to exclude files (e.g., `.git`, `node_modules`). | `Filter: func(p string) bool { return !strings.HasPrefix(filepath.Base(p), ".") }` |

---

## 6. Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Language** | Go 1.22+ | Fast, single binary, excellent git tooling. |
| **Git plumbing** | `go-git` (github.com/go-git/go-git/v5) | Pure Go, no external `git` binary. |
| **Archive** | `archive/tar`, `compress/gzip` (std lib) | Reliable, no external deps. |
| **CLI** | `spf13/cobra` | Mature flag parsing, help generation. |
| **Testing** | `testing`, `stretchr/testify` | Unit & integration tests. |
| **CI** | GitHub Actions | Build, test, release. |
| **Packaging** | `goreleaser` | Cross‑platform binaries, GitHub releases. |

---

## 7. Dependencies

| Dependency | Version | License | Notes |
|------------|---------|---------|-------|
| `github.com/go-git/go-git/v5` | v5.4.0 | BSD-3-Clause | Git plumbing. |
| `github.com/spf13/cobra` | v1.6.1 | BSD-3-Clause | CLI framework. |
| `github.com/stretchr/testify` | v1.8.3 | BSD-3-Clause | Test assertions. |
| `github.com/goreleaser/goreleaser` | v2.0.0 | MIT | Release tooling. |

All dependencies are vendored via Go modules (`go mod vendor`) to ensure reproducibility.

---

## 8. Deployment & Release

1. **Local Build**  
   ```bash
   go build -o code-archive ./cmd/code-archive
   ```

2. **Cross‑Platform Release**  
   ```bash
   goreleaser release --snapshot --skip-publish
   ```

3. **Installation**  
   - Binary download from GitHub Releases.  
   - Or via Homebrew tap: `brew install axentx/tap/code-archive`.

4. **Configuration**  
   - No external config files; all options via CLI flags.

5. **Environment Variables**  
   - `CODE_ARCHIVE_LOG_LEVEL` – `debug`, `info`, `warn`, `error`.  
   - `CODE_ARCHIVE_TMP_DIR` – custom temp directory for cloning.

---

## 9. Security & Compliance

- **No network access** except for cloning the target repo (HTTPS/SSH).  
- **No credentials** are stored; SSH keys must be available in the environment.  
- **Checksum** guarantees integrity; SHA‑256 is exposed in `metadata.json`.  
- **No external binaries** – mitigates supply‑chain risk.

---

## 10. Future Enhancements

| Feature | Status | Notes |
|---------|--------|-------|
| **Parallel file extraction** | Planned | Speed up large repos. |
| **S3/HTTP upload** | Planned | Direct snapshot upload. |
| **Incremental snapshots** | Planned | Store diffs between commits. |
| **Plugin system** | Planned | Custom filters, post‑process hooks. |

---

## 11. Contact & Support

- **Repository**: `arkashira/code-archive`  
- **Issue Tracker**: GitHub Issues  
- **Slack**: #code-archive (Axentx internal)  
- **Email**: support@axentx.com  

---
