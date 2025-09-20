# GitHub Activity CLI

A simple command-line interface (CLI) to fetch and display the recent public activity of any GitHub user.

## Features
- Fetches recent public GitHub activity of any user.
- Supports filtering by:
  - Pushes
  - Issues
  - Pull requests
  - Issue comments
  - Stars (watch events)
  - Forks
- Displays timestamps in local time.
- Handles errors gracefully (user not found, rate limit exceeded, network issues).
- Supports GitHub token via environment variable to avoid rate limit restrictions.

## Inspiration
This project idea comes from [roadmap.sh](https://roadmap.sh) — a community-driven site that provides developer projects and learning roadmaps.  
Original project link: [GitHub User Activity CLI](https://roadmap.sh/projects/github-user-activity)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Arshiya-Bagheri/github-activity.git
   cd github_activity
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the CLI:
```bash
python cli.py
```

Available commands:
```
<username>              Show all recent activity
<username> push         Show push events
<username> issues       Show issues activity
<username> pullrequest  Show pull request activity
<username> issuecomment Show issue comments
<username> watch        Show stars
<username> fork         Show forks
help                    Show help menu
start                   Show the introduction to the CLI.
exit / quit             Exit the CLI
```

## Example
```bash
github-activity> Arshiya-Bagheri push
🟢 Pushed 3 commits to Arshiya-Bagheri/task-manager at 2025-09-20 14:12:33
```

## Project Structure

```
github-activity/
├── github_activity/           # Main Python package
│   ├── __init__.py
│   └── cli.py                 # Main CLI application
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_cli.py
├── dist/                      # PyInstaller output (ignored in Git)
├── build/                     # PyInstaller temporary build files (ignored)
├── .gitignore                 # Git ignore file
├── requirements.txt           # Dependencies (e.g., requests)
├── LICENSE                    # License file (MIT)
└── README.md                  # Project documentation

```

## License
This project is licensed under the MIT License.  
You are free to use, modify, and distribute this project.
