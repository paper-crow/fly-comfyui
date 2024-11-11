import yaml
import os
import subprocess

def clone_custom_nodes(workflows_path):
    # Read the YAML file
    with open(workflows_path, 'r') as file:
        workflows = yaml.safe_load(file)
    
    # Create custom_nodes directory if it doesn't exist
    os.makedirs('custom_nodes', exist_ok=True)
    
    # Keep track of valid custom node names
    valid_node_names = set()
    
    # Iterate through workflows
    for workflow in workflows:
        # Skip only if enabled is explicitly set to False
        if workflow.get('enabled') is False:
            print(f"Skipping workflow '{workflow.get('name', 'Unnamed')}': not enabled")
            continue
        
        # Skip if no custom_nodes defined
        if 'custom_nodes' not in workflow:
            continue
            
        # Clone each custom node repository
        for node in workflow['custom_nodes']:
            valid_node_names.add(node['name'])
            target_dir = os.path.join('custom_nodes', node['name'])
            
            # Skip if already cloned
            if os.path.exists(target_dir):
                print(f"Skipping {node['name']}: already exists")
                continue
                
            # Base clone command
            cmd = ['git', 'clone', '--depth', '1']
            
            # Add branch parameter if specified
            if 'branch' in node:
                cmd.extend(['-b', node['branch']])
            
            # Add recursive flag if specified
            if node.get('recursive', False):
                cmd.append('--recursive')
            
            # Add URL and target directory
            cmd.extend([node['url'], target_dir])
            
            try:
                # Clone the repository
                subprocess.run(cmd, check=True)
                print(f"Cloned {node['name']} successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone {node['name']}: {e}")
    
    # Remove directories that aren't in the workflows
    for dir_name in os.listdir('custom_nodes'):
        dir_path = os.path.join('custom_nodes', dir_name)
        if os.path.isdir(dir_path) and dir_name not in valid_node_names:
            print(f"Removing {dir_name}: no longer in workflows")
            subprocess.run(['rm', '-rf', dir_path], check=True)

# Usage
clone_custom_nodes('workflows.yml')