#!/usr/bin/env python3
"""
Fix kubeconfig to use aws via Python instead of requiring aws executable in PATH
"""
import yaml
import subprocess
import sys

kubeconfig_path = os.path.expanduser("~/.kube/config")

# Read kubeconfig
with open(kubeconfig_path, 'r') as f:
    config = yaml.safe_load(f)

# Update the exec command to use python -m awscli
for user in config.get('users', []):
    if 'exec' in user.get('user', {}):
        exec_config = user['user']['exec']
        # Replace 'aws' with full Python command
        if exec_config.get('command') == 'aws':
            exec_config['command'] = sys.executable
            exec_config['args'] = ['-m', 'awscli'] + exec_config.get('args', [])
        elif 'aws' in exec_config.get('command', ''):
            exec_config['command'] = sys.executable
            exec_config['args'] = ['-m', 'awscli', 'eks', 'get-token'] + exec_config.get('args', [])[2:]

# Write back
with open(kubeconfig_path, 'w') as f:
    yaml.dump(config, f)

print(f"Updated {kubeconfig_path}")
print("Try: kubectl get nodes")
