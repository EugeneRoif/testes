import requests
from bs4 import BeautifulSoup

# Set variables
host = "localhost"
port = "8888"
credentials_file = "/home/hadoop/hue-config/hue_access_admin.txt"  # password file
user = "admin"
protocol = "http"

def get_password(file_path):
    """
    Reads the password from a text file.

    Args:
        file_path (str): Path to the password file.

    Returns:
        str: The password.
    """
    with open(file_path, 'r') as f:
        return f.read().strip()

def login(host, port, credentials_file):
    """
    Logs into Hue using the provided credentials.

    Args:
        host (str): Hostname or IP address of the server.
        port (int): Port number to use.
        credentials_file (str): Path to the password file.

    Returns:
        str: The CSRF token value.
    """
    password = get_password(credentials_file)

    # Log into Hue
    login_response = requests.post(f"{protocol}://{host}:{port}/hue/accounts/login/?fromModal=true",
                                   data={"username": user, "password": password})

    return BeautifulSoup(login_response.text, 'html.parser').find('input', attrs={'name': 'csrftoken'}).attrs['value']

def set_group_permissions(host, port, credentials_file, group_name, permissions):
    """
    Sets the permissions for a group in Hue.

    Args:
        host (str): Hostname or IP address of the server.
        port (int): Port number to use.
        credentials_file (str): Path to the password file.
        group_name (str): Name of the group to modify.
        permissions (list): List of permission IDs to assign.
    """
    # Get CSRF token
    csrf_token = login(host, port, credentials_file)

    # Set group permissions
    response = requests.post(f"{protocol}://{host}:{port}/useradmin/groups/edit/{group_name}",
                             data={"csrfmiddlewaretoken": csrf_token,
                                   "name": group_name},
                             headers={'X-CSRFToken': csrf_token})

    # Parse HTML response to get permission IDs
    soup = BeautifulSoup(response.text, 'html.parser')
    permissions_ids_input = soup.find('input', attrs={'name': 'permissions'})

    if permissions_ids_input:
        for permission_id in permissions:
            permissions_ids_input.attrs['value'] += f"&permissions={permission_id}"

        # Update request with modified permissions
        requests.post(f"{protocol}://{host}:{port}/useradmin/groups/edit/{group_name}",
                      data=permissions_ids_input.attrs,
                      headers={'X-CSRFToken': csrf_token})

# Set variables
credentials_file = "/home/hadoop/hue-config/hue_access_admin.txt"  # password file
group_name = "spark02-user"
permissions_id1 = "10"  # jobbrowser.access
permissions_id2 = "18"  # spark.access

set_group_permissions(host, port, credentials_file, group_name, [permissions_id1, permissions_id2])
