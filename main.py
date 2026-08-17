"""Command-line interface for the weather application."""

import argparse
import requests

import github_activity.api



def main():
    parser = argparse.ArgumentParser(
        prog="Github-Activity API",
        description="A simple command-line Github-Activity application"
    )

    parser.add_argument(
        "username",
        help="GitHub username to fetch activity for"
    )

    args = parser.parse_args()

    data = github_activity.api.get_user_events(args.username)

    print(type(data))
    print(data[0]["type"])
    print(data[0]["repo"]["name"])
    print(data[0]["created_at"])



if __name__ == "__main__":
    main()