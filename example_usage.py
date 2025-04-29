import os
from typing import Dict, Optional

from standalone_taskweaver import AppConfigSource, TaskWeaverApp
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing


def main():
    """
    IMPORTANT: Before running this example, install the required dependencies:
    
    pip install -r requirements.txt
    
    If you encounter any issues, make sure all dependencies are properly installed.
    """
    # Create the app config
    config = AppConfigSource(
        app_base_path=os.path.dirname(os.path.abspath(__file__)),
    )

    # Create the logger
    logger = TelemetryLogger(
        log_dir=os.path.join(config.app_base_path, "logs"),
    )

    # Create the tracing
    tracing = Tracing()

    # Create the app
    app = TaskWeaverApp(
        config=config,
        logger=logger,
        tracing=tracing,
    )

    # Create a session
    session = app.create_session(
        session_name="Example Session",
    )

    # Chat with the session
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        response = session.chat(user_input)
        print(f"TaskWeaver: {response}")

    # Close the session
    session.close()


if __name__ == "__main__":
    main()
