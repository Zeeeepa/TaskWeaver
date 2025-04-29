#!/usr/bin/env python3
"""
Example usage of the standalone TaskWeaver module.
"""

from standalone_taskweaver import AppConfigSource, TaskWeaverApp

def main():
    """Main function demonstrating TaskWeaver usage"""
    # Create a configuration source
    config_source = AppConfigSource()
    
    # Initialize the TaskWeaver app
    app = TaskWeaverApp(config_source)
    
    # Create a new session
    session = app.create_session("example_session")
    
    # Chat with TaskWeaver
    print("TaskWeaver is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # Get response from TaskWeaver
        response = session.chat(user_input)
        print(f"TaskWeaver: {response}")
    
    # Close the session
    session.close()

if __name__ == "__main__":
    main()

