import argparse

import github_activity.api



def create_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="Github-Activity API",
        description="A simple command-line Github-Activity application"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands"
    )

    







def main():
    pass




if __name__ == "__main__":
    main()