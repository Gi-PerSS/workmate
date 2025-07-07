from project.controller.dispatcher import CLIArgumentsDispatcher 

if __name__ == "__main__":
    try:
        CLIArgumentsDispatcher.run()
    except Exception as e:
        print(f"Error occurred: {e}")
