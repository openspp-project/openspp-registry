import logging
import os
import re
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_linting():
    """Run the linting command and return the output."""
    result = subprocess.run(["pre-commit", "run", "pylint_odoo", "--all-files"], capture_output=True, text=True)
    return result.stdout


def parse_linting_output(output):
    """Parse the linting output to get a dictionary of files with issues and their errors."""
    files_with_issues = {}
    current_module = None
    for line in output.splitlines():
        if line.startswith("************* Module"):
            current_module = line.split()[-1]
            continue

        match = re.match(r"([^:]+):(\d+): \[(\w+)\(([^)]+)\), ([^\]]+)\] (.+)", line)
        if match:
            file_path, line_number, error_code, error_type, context, error_message = match.groups()

            if current_module:
                file_path = os.path.join(current_module, file_path)

            if file_path not in files_with_issues:
                files_with_issues[file_path] = []

            files_with_issues[file_path].append(
                {
                    "line_number": int(line_number),
                    "error_code": error_code,
                    "error_type": error_type,
                    "context": context,
                    "error_message": error_message,
                }
            )
    return files_with_issues


def extract_lines_from_file(file_path, errors):
    """Extract the relevant lines from the file based on the error information."""
    with open(file_path) as file:
        lines = file.readlines()

    extracted_lines = []
    for error in errors:
        line_number = error["line_number"]
        if 0 <= line_number - 1 < len(lines):
            line_content = lines[line_number - 1].strip()
            extracted_lines.append(
                {
                    "line_number": line_number,
                    "content": line_content,
                    "error_code": error["error_code"],
                    "error_type": error["error_type"],
                    "context": error["context"],
                    "error_message": error["error_message"],
                }
            )
        else:
            logger.warning(f"Line number {line_number} is out of range for file {file_path}")
            extracted_lines.append(
                {
                    "line_number": line_number,
                    "content": "Unable to extract line content",
                    "error_code": error["error_code"],
                    "error_type": error["error_type"],
                    "context": error["context"],
                    "error_message": error["error_message"],
                }
            )

    return extracted_lines


def fix_file_with_aider(file_path, errors):
    """Use Aider to fix the file with the provided errors."""
    extracted_lines = extract_lines_from_file(file_path, errors)

    error_instructions = """
Please fix the following linting errors in my Odoo project. Pay careful attention to these guidelines:

1. ONLY modify the specific lines provided below. Do not change any other part of the file.
2. For each error, I will provide the line number, the current content of the line, the error code,
    type, context, and message.
3. Your task is to fix each line according to the error message, while preserving the intended functionality.
4. For 'print-used' errors, replace print statements with appropriate logger calls.
5. If you're unsure how to fix an error, leave the line as is and add a comment explaining why.

Here are the specific lines to fix:

"""
    for line in extracted_lines:
        error_instructions += f"""
Line {line['line_number']}:
Current content: {line['content']}
Error code: {line['error_code']}
Error type: {line['error_type']}
Context: {line['context']}
Error message: {line['error_message']}

"""

    error_instructions += "\nPlease provide the fixed version of each line, or explain why you chose not to modify it."

    logger.info(f"Fixing {file_path} with Aider")
    logger.info(error_instructions)

    command = [
        "/Users/jeremi/.virtualenvs/aider2/bin/aider",
        "--4o",
        "--no-auto-commits",
        "--yes",
        file_path,
        "--message",
        error_instructions,
    ]
    logger.info(f"Running command: {' '.join(command)}")
    subprocess.run(command)


def main():
    linting_output = run_linting()
    files_with_issues = parse_linting_output(linting_output)

    for file_path, errors in files_with_issues.items():
        fix_file_with_aider(file_path, errors)


if __name__ == "__main__":
    main()
