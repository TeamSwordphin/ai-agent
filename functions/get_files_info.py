import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    try:
        abs_path = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_path, directory))
        validate = os.path.commonpath([abs_path, target_dir]) == abs_path

        if validate == False:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        file_str = f"Result for {"current" if directory == "." else f"'{directory}'"} directory:"

        for item in os.listdir(target_dir):
            if item == "__pycache__":
                continue

            item_path = target_dir + "/" + item
            size = os.path.getsize(item_path)
            is_file = os.path.isfile(item_path)
            file_str = f"{file_str}\n - {item}: file_size={size} bytes, is_dir={not is_file}"

        return file_str

    except Exception as e:
        return f"Error: {e}"