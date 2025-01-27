import sys
from app import app as application

# Add your project directory to the sys.path
project_home = '/home/yourusername/yourprojectname'
if project_home not in sys.path:
    sys.path.append(project_home) 