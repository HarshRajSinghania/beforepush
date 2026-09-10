import argparse

from checks import run_checks
from output import display_results


def main():
    parser = argparse.ArgumentParser(
        description="Check whether your Git branch is ready before pushing or opening a PR."
    )

    parser.add_argument(
        "--target",
        default="main",
        help="Target branch to compare against (default: main)",
    )

    args = parser.parse_args()

    results = run_checks(args.target)
    display_results(results, args.target)


if __name__ == "__main__":
    main()