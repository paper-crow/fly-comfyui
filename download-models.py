import os
import requests
import yaml
from typing import Set, Dict

# Load the workflows from the YAML file
with open('workflows.yml', 'r') as file:
    workflows = yaml.safe_load(file)

# Base directory for downloads
base_dir = 'models'

# Keep track of all valid models from YAML
valid_models: Dict[str, Set[str]] = {}

# First, build a set of all valid models from YAML (only from enabled workflows)
for workflow in workflows:
    # Skip if enabled is explicitly set to False
    if workflow.get('enabled') is False:
        print(f"Skipping workflow '{workflow.get('name', 'Unnamed')}': not enabled")
        # Don't add models from disabled workflows to valid_models
        continue
        
    for model_type, models in workflow.get('models', {}).items():
        if model_type not in valid_models:
            valid_models[model_type] = set()
        for model in models:
            valid_models[model_type].add(model['name'])

# Download models and clean up old ones
for workflow in workflows:
    # Skip if enabled is explicitly set to False
    if workflow.get('enabled') is False:
        continue
        
    # Get all model types from the workflow
    model_types = workflow.get('models', {}).keys()
    
    # Process each model type
    for model_type in model_types:
        # Create directory for this model type
        type_dir = os.path.join(base_dir, model_type)
        os.makedirs(type_dir, exist_ok=True)
        
        # Download each model of this type
        for model in workflow['models'][model_type]:
            model_name = model['name']
            model_url = model['url']
            model_path = os.path.join(type_dir, model_name)
            model_file_path = os.path.join(type_dir, model_name)
            
            # Skip if model already exists
            if os.path.exists(model_file_path):
                print(f'⏭️  Skipping {model_name} - already exists')
                continue
            
            # Download the model
            print(f'⬇️  Downloading {model_name}...')
            headers = {}
            
            # Handle CivitAI authentication
            if 'civitai.com' in model_url:
                civitai_token = os.getenv('CIVITAI_TOKEN')
                if civitai_token:
                    headers['Authorization'] = f'Bearer {civitai_token}'
                else:
                    print(f'❌ CIVITAI_TOKEN environment variable not set - cannot download {model_name}')
                    continue
            
            # Handle Hugging Face authentication
            elif 'huggingface.co' in model_url:
                hf_token = os.getenv('HUGGINGFACE_TOKEN')
                if hf_token:
                    headers['Authorization'] = f'Bearer {hf_token}'
                else:
                    print(f'❌ HUGGINGFACE_TOKEN environment variable not set - cannot download {model_name}')
                    continue
                    
            response = requests.get(model_url, stream=True, headers=headers)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 256 * 1024  # 256KB chunks - better balanced for most systems
                with open(model_file_path, 'wb') as model_file:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            model_file.write(chunk)
                            downloaded += len(chunk)
                            if downloaded % (50 * 1024 * 1024) == 0:  # Still show progress every 50MB
                                progress = (downloaded / total_size) * 100 if total_size else 0
                                print(f'    Progress: {progress:.1f}% ({downloaded // (1024*1024)}MB)')
                print(f'✅ Downloaded {model_name} to {model_path}')
            else:
                print(f'❌ Failed to download {model_name} from {model_url}')

# Clean up old models (this part remains unchanged but will now remove models 
# from disabled workflows since they weren't added to valid_models)
for model_type in os.listdir(base_dir):
    type_dir = os.path.join(base_dir, model_type)
    if not os.path.isdir(type_dir):
        continue
        
    # Skip if this model type isn't in our YAML at all
    if model_type not in valid_models:
        continue
    
    # Check each model file
    for model_name in os.listdir(type_dir):
        model_path = os.path.join(type_dir, model_name)
        if model_name not in valid_models[model_type]:
            print(f'🗑️  Removing unused model: {model_path}')
            os.remove(model_path)