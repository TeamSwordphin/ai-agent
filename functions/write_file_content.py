import os
from google.genai import types

schema_write_file_content = types.FunctionDeclaration(
    name="write_file_content",
    description="Get and write to a file's content.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        required=["file_path", "content"],
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The actual name of the file, plus the file extension.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content as text to write the file with.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    try:
        abs_path = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_path, file_path))
        validate = os.path.commonpath([abs_path, target_dir]) == abs_path

        if validate == False:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_dir):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        os.makedirs(os.path.dirname(target_dir), exist_ok=True)

        with open(target_dir, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
            
    except Exception as e:
        return f"Error: {e}"