# GitHub Activity CLI

A modern, formatted command-line interface (CLI) for fetching, filtering, and inspecting recent public GitHub activity for any user.

Built with Python, the GitHub REST API, and [Rich](https://github.com/Textualize/rich), this project transforms raw GitHub event data into clean, readable terminal output or structured JSON.

---

## Features

- **Rich Terminal UI**
  - Formatted tables
  - Status icons
  - Colors and styling
  - Relative timestamps
  - Event counts

- **Multiple Output Formats**
  - Human-readable terminal output powered by Rich
  - Structured JSON output with `--format json`

- **Event Filtering**
  - Filter by event type
  - Filter by repository
  - Filter by date range
  - Limit the number of returned events

- **Repository Filtering**
  - Supports exact `owner/repository` matches
  - Supports short repository-name matches

- **Date Filtering**
  - Filter events using `--since`
  - Filter events using `--until`
  - Uses `YYYY-MM-DD` date format

- **Pagination**
  - Automatically requests multiple pages from the GitHub API when necessary
  - Supports retrieving up to 300 events

- **Retry Handling**
  - Automatically retries failed requests
  - Handles GitHub rate-limit responses such as `403` and `429`
  - Uses backoff between retry attempts

- **Error Handling**
  - Clear messages for invalid usernames
  - Handles GitHub API errors
  - Handles network failures
  - Validates CLI arguments and date formats

- **Automated Testing**
  - Comprehensive test suite using `pytest`
  - Tests API behavior, filtering, event handling, CLI arguments, models, and output formatting

---

## Inspiration

This project implements and extends the
[GitHub User Activity](https://roadmap.sh/projects/github-user-activity)
project idea from [roadmap.sh](https://roadmap.sh).

The original project focuses on retrieving a user's recent GitHub activity. This implementation goes further by adding filtering, pagination, retry handling, Rich terminal formatting, JSON output, and automated tests.

---

## Requirements

- Python 3.10+
- Internet connection
- A public GitHub username

The application uses the public GitHub REST API and does not require a GitHub authentication token for basic usage.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Arshiya-Bagheri/github-activity.git
cd github-activity
```

### 2. Create a virtual environment

Creating a virtual environment is recommended:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

Run the CLI with:

```bash
python main.py <username> [options]
```

For example:

```bash
python main.py torvalds
```

---

## CLI Arguments & Options

| Argument / Flag | Type | Description |
| :--- | :--- | :--- |
| `username` | `str` | **Required.** GitHub username whose activity will be inspected. |
| `--limit N` | `int` | Maximum number of events to retrieve and display. Range: `1–300`. |
| `--event TYPE` | `str` | Filter events by event type. |
| `--repo REPOSITORY` | `str` | Filter events by repository name. Supports `repo` or `owner/repo`. |
| `--since DATE` | `YYYY-MM-DD` | Include events occurring on or after this date. |
| `--until DATE` | `YYYY-MM-DD` | Include events occurring on or before this date. |
| `-f`, `--format FORMAT` | `text \| json` | Select the output format. Defaults to `text`. |

### Getting Help

To display all available options:

```bash
python main.py --help
```

---

## Supported Event Types

The `--event` option supports the following GitHub event types:

| Value | GitHub Event | Description |
| :--- | :--- | :--- |
| `push` | `PushEvent` | Commits pushed to a repository branch |
| `issues` | `IssuesEvent` | Issues opened, edited, or closed |
| `pullrequest` | `PullRequestEvent` | Pull requests opened, closed, or merged |
| `issuecomment` | `IssueCommentEvent` | Comments posted on issues or pull requests |
| `watch` | `WatchEvent` | A repository is starred |
| `fork` | `ForkEvent` | A repository is forked |
| `create` | `CreateEvent` | Branches, tags, or repositories created |
| `delete` | `DeleteEvent` | Branches or tags deleted |
| `release` | `ReleaseEvent` | A repository release is published |
| `public` | `PublicEvent` | A repository is made public |

---

## Examples

### 1. View recent activity

```bash
python main.py torvalds
```

This displays recent public activity using the default Rich terminal interface.

### 2. Show only push events

```bash
python main.py torvalds --event push
```

### 3. Limit the number of events

```bash
python main.py torvalds --limit 10
```

### 4. Filter by repository

Using a short repository name:

```bash
python main.py torvalds --repo linux
```

Or using the full repository name:

```bash
python main.py torvalds --repo torvalds/linux
```

### 5. Filter by date range

```bash
python main.py torvalds --since 2026-01-01 --until 2026-08-01
```

### 6. Combine multiple filters

```bash
python main.py torvalds --event push --repo linux --limit 10
```

### 7. Output activity as JSON

```bash
python main.py torvalds --format json
```

JSON output can also be combined with filters:

```bash
python main.py torvalds --event issues --limit 20 --format json
```

This makes the output suitable for scripting, processing, or piping into other tools.

---

## Example Output

### Rich Terminal Output

```text
GitHub Activity: torvalds

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time               ┃ Event         ┃ Repository                   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2 hours ago        │ PUSH          │ torvalds/linux               │
│ 5 hours ago        │ ISSUE         │ torvalds/linux               │
│ 1 day ago          │ PULL REQUEST  │ torvalds/linux               │
└────────────────────┴───────────────┴──────────────────────────────┘
```

The exact output depends on the user's recent GitHub activity.

### JSON Output

```json
[
  {
    "type": "PushEvent",
    "repo": "torvalds/linux",
    "created_at": "2026-08-20T12:34:56Z"
  }
]
```

The exact JSON structure depends on the normalized activity model and the events returned by GitHub.

---

## How It Works

The application follows a simple processing pipeline:

```text
GitHub Username
       │
       ▼
GitHub REST API
       │
       ▼
API Client
       │
       ├── Pagination
       ├── Retry Handling
       └── Error Handling
       │
       ▼
Event Handler
       │
       ▼
Activity Models
       │
       ▼
Filtering & Sorting
       │
       ├───────────────┐
       ▼               ▼
   Rich Output      JSON Output
```

### 1. Fetch

The API client requests public GitHub events for the specified username.

### 2. Normalize

Raw GitHub API events are converted into application-level `Activity` models.

### 3. Filter

The activity layer applies the requested filters:

- Event type
- Repository
- Start date
- End date
- Result limit

### 4. Format

The processed activities are converted into either:

- Rich terminal output
- JSON output

This separation keeps API communication, business logic, data models, and presentation code independent from each other.

---

## Project Structure

```text
github-activity/
├── github_activity/
│   ├── __init__.py          # Package metadata and version information
│   ├── activity.py          # Filtering, sorting, and high-level workflow
│   ├── api.py               # GitHub REST API client and retry logic
│   ├── exports.py           # Rich terminal output and JSON serialization
│   ├── handler.py           # Raw GitHub event normalization
│   └── models.py            # Activity data models
│
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   ├── test_activity.py     # Filtering, dates, sorting, and activity logic
│   ├── test_api.py          # API client and request behavior
│   ├── test_cli.py          # CLI argument parsing and error handling
│   ├── test_exports.py      # Output formatting and serialization
│   ├── test_handler.py      # Event conversion and normalization
│   └── test_models.py       # Activity model tests
│
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## Architecture

The project is divided into several layers:

### `api.py`

Responsible for communicating with the GitHub REST API.

It handles:

- HTTP requests
- Pagination
- Timeouts
- Retry behavior
- API errors

### `handler.py`

Responsible for converting raw GitHub API events into a consistent internal representation.

This keeps GitHub-specific event structures out of the rest of the application.

### `models.py`

Defines the application's data models using Python dataclasses.

This provides a consistent structure for working with activity data throughout the project.

### `activity.py`

Contains the main application logic.

It handles:

- Filtering
- Sorting
- Date boundaries
- Repository matching
- Event-type matching
- Result limits

### `exports.py`

Responsible for presenting the processed activity.

It supports:

- Rich terminal tables
- JSON serialization

### `main.py`

Acts as the CLI entry point.

It is responsible for:

- Parsing command-line arguments
- Validating user input
- Connecting the CLI to the application layer
- Displaying appropriate errors

---

## Testing

The project uses [pytest](https://docs.pytest.org/) for automated testing.

The test suite covers:

- Activity filtering
- Date filtering
- Repository matching
- Event-type filtering
- Event normalization
- API request behavior
- Retry handling
- CLI argument parsing
- Error handling
- Data models
- Rich output
- JSON serialization

Run the complete test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

---

## Technologies Used

- **Python** — Application language
- **GitHub REST API** — Source of public GitHub activity
- **Rich** — Terminal formatting and UI
- **argparse** — Command-line argument parsing
- **pytest** — Automated testing

---

## Learning Goals

This project was built to practice and strengthen several Python and software-development concepts:

- Working with REST APIs
- HTTP requests and error handling
- JSON data processing
- Command-line interfaces
- `argparse`
- Python dataclasses
- Modular application architecture
- Filtering and sorting data
- Pagination
- Retry and backoff strategies
- Automated testing with `pytest`
- Mocking external API requests
- Terminal UI development with Rich
- Git and GitHub workflow

---

## License

This project is licensed under the [MIT License](LICENSE).