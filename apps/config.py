import os
from dotenv import load_dotenv


load_dotenv()


GITHUB_CLIENT_ID = os.environ.get('github-client-id', None)
GITHUB_CLIENT_SECRET = os.environ.get('github-client-secret', None)



print("GITHUB_CLIENT_ID:", GITHUB_CLIENT_ID)
print("GITHUB_CLIENT_SECRET:", GITHUB_CLIENT_SECRET)