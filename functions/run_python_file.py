import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Get and run a python file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        required=["file_path"],
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The actual name of the file, plus the file extension.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Arguments to run with.",
                items=types.Schema(
                    type=types.Type.STRING
                )
            ),
        },
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        abs_path = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_path, file_path))
        validate = os.path.commonpath([abs_path, target_dir]) == abs_path

        if validate == False:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_dir.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_dir]

        if args is not None:
            command.extend(list(args))

        completed_process = subprocess.run(command, timeout=30, text=True, capture_output=True)
        content = ""

        if completed_process.returncode != 0:
            content += f"Process exited with code {completed_process.returncode}"

        if completed_process.stdout == "" and completed_process.stderr == "":
            content += "\nNo output produced"
        else:
            if completed_process.stdout != "":
                content += f"\nSTDOUT: {completed_process.stdout}"

            if completed_process.stderr != "":
                content += f"\nSTDERR: {completed_process.stderr}"

        return content
            
    except Exception as e:
        return f"Error: executing Python file: {e}"