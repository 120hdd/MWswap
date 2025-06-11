# main_runner.py
import os
import importlib.util
import questionary
from config import MODULE_PATH

def load_and_run_module(module_path):
    """
    Load a module from the given path and run its main function.
    """
    # Extract the module name from the path
    module_name = os.path.basename(module_path).replace('.py', '')

    # Load the module using importlib
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Run the module's main function if it exists
    if hasattr(module, 'main'):
        print(f"Running main() from {module_name}...")
        module.main()
    else:
        print(f"No main() function found in {module_name}. Skipping...")

def run_selected_module():
    """
    Allow the user to select which module to run from the available Python files.
    """
    # Check if the specified path is a directory
    #reza
    if os.path.isdir(MODULE_PATH):
        # Get all Python files in the directory
        python_files = [f for f in os.listdir(MODULE_PATH) if f.endswith('.py')]

        if not python_files:
            print("No Python modules found in the specified directory.")
            return
    
        # Use questionary to ask the user to select a module to run
        selected_file = questionary.select(
            "Select the module you want to run:",
            choices=python_files
        ).ask()

        if selected_file:
            # Construct the full path of the selected module
            module_path = os.path.join(MODULE_PATH, selected_file)
            try:
                load_and_run_module(module_path)
            except Exception as e:
                print(f"Error running {module_path}: {e}")
        else:
            print("No module selected.")
    else:
        print(f"The path '{MODULE_PATH}' is not a valid directory.")

if __name__ == "__main__":
    run_selected_module()


 