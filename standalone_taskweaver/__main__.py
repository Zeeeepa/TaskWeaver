#!/usr/bin/env python3
"""
Main entry point for TaskWeaver.
"""

from standalone_taskweaver.app import create_app


def main() -> None:
    """
    Main entry point for TaskWeaver.
    """
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()

