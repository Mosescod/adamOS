import requests
import os

# Set your Atlas API keys
PUBLIC_KEY = "your_public_key"
PRIVATE_KEY = "your_private_key"
GROUP_ID = "your_project_id"  # Find in Project Settings

# Get current IP
current_ip = requests.get('https://api.ipify.org').text

# Check against Atlas whitelist
auth = requests.auth.HTTPDigestAuth(PUBLIC_KEY, PRIVATE_KEY)
response = requests.get(
    f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{GROUP_ID}/accessList",
    auth=auth
)

whitelisted = any(
    entry['ipAddress'] == current_ip 
    for entry in response.json()['results']
)

print(f"IP {current_ip} is {'whitelisted' if whitelisted else 'NOT whitelisted'}")