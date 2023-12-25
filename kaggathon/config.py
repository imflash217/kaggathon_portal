from pathlib import Path
from kaggathon.examples.dummy_metrics_evaluator import ExampleEvaluator


# the directory in which user's submission will be saved
SUBMISSIONS_DIR = Path(__file__).parent.parent.absolute() / "user_submissions"

# the name of the encrypted PASSWORDS file
PASSWORDS_DB_FILE = Path(__file__).parent.parent.absolute() / "passwords.db"

# we'll be using ARGON2's python client for password hashing and authentication
ARGON2_KWARGS = {}

# Maximum number of users allowed in the system.
# If None, no limitation is enforced.
MAX_NUM_USERS = None

# the file extension used for submission
# if None, any file extension is allowed.
VALID_SUBMISSION_FILE_EXTENSION = "json"

SHOW_TOP_K_ONLY = 5
ADMIN_USERNAME = "admin"

# evaluation criteria and metrics
EVALUATOR_CLASS = ExampleEvaluator
EVALUATOR_KWARGS = {}
