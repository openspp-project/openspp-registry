import logging
import os
import re
import sys
import xmlrpc.client

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Sanitize user inputs
def sanitize(input_string):
    return re.sub(r"[^a-zA-Z0-9 ]", "", input_string)


# Ensure the URL is correctly formatted
url = os.getenv("ODOO_URL")
if not url.startswith("http://") and not url.startswith("https://"):
    logger.error("Error: ODOO_URL should start with http:// or https://")
    sys.exit(1)

db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")  # Odoo login username
password = os.getenv("ODOO_PASSWORD")  # API Key is used
project_name = "OpenSPP"  # Project name in Odoo
issue_title = sanitize(os.getenv("TITLE", "")[:256])
issue_body = sanitize(os.getenv("BODY", "")[:256])
github_issue_id = sanitize(os.getenv("ISSUE", "")[:256])

# XML-RPC endpoints for Odoo
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Authenticate with Odoo
uid = common.authenticate(db, username, password, {})

# Search for the project by name to get its ID
project_id = models.execute_kw(
    db, uid, password, "project.project", "search", [[["name", "=", project_name]]], {"limit": 1}
)

if not project_id:
    logger.error("Project not found")
    sys.exit(1)

# Check if a task with the given GitHub issue ID already exists
task_id = models.execute_kw(
    db, uid, password, "project.task", "search", [[["x_github_issue_id", "=", github_issue_id]]], {"limit": 1}
)

if task_id:
    # Update the existing task
    models.execute_kw(
        db,
        uid,
        password,
        "project.task",
        "write",
        [
            task_id,
            {
                "name": issue_title,
                "description": issue_body,
            },
        ],
    )
    logger.info(f"Task updated with ID: {task_id[0]}")
else:
    # Create a new task
    task_id = models.execute_kw(
        db,
        uid,
        password,
        "project.task",
        "create",
        [
            {
                "name": issue_title,
                "description": issue_body,
                "project_id": project_id[0],
                "x_github_issue_id": github_issue_id,  # Set the GitHub issue ID
            }
        ],
    )
    logger.info(f"Task created with ID: {task_id}")
