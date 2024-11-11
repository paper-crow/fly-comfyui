# ComfyUI on Fly.io

> **NOTE: This will launch a ComfyUI app on the Fly.io public cloud so it will be accessible by anyone on the internet.**

## Setup

By default this will use Fly's `l40s` GPU on a `performance-8x` machine with `16GB` of memory. You can change this configuration by editing the [`fly.toml`](fly.toml) file.

To get started, run:

```
fly launch
```

## Scaling

> Once the app is launched, it will scale to 0 when idle. However, since it is publically accessible, you should manually scale it to `0` when you are not using it.

```
fly scale count 0 -y
```

To scale it back up for use you can run:

```
fly scale count 1 -y
```

## Custom Node and Model Management

You can use the `workflows.yml` file to manage custom nodes and models. This will automatically download and install any custom nodes and models that are specified in the file. The models will be downloaded in the background so you will have to wait for them to finish before you can use them. Their progress is reported to the console so you can use `fly logs` to see the progress.

I have grouped it by a "workflow" concept as a way to manage different configurations of nodes and models. For example, you might have a workflow for "default" which has all the nodes and models that you commonly use. Then you could have another workflow for "portrait" which enables nodes and models that are useful for generating portriats. This does not "toggle" nodes on and off based on the workflow, all nodes and models are aggregated and downloaded when you deploy the app.

> As I have been learning I have needed a way to keep track of the models and nodes needed for each tutorial I follow, along with a way to easily clean up the models and nodes that I no longer use.

You can add your own workflows by adding them to the `workflows.yml` file and then running `fly deploy` to redeploy the app.

Should you remove a node or model from the workflow, it will be automatically removed from the persistent storage for the app.

```yaml
# workflows.yml
- name: 
  description: 
  enabled: true
  custom_nodes: []
  models:
```

**Cleanup**

If you remove a node or model from the workflow, it will be automatically removed from the persistent storage for the app when you redeploy the app.

### Custom Nodes

Should your node require additional dependencies, you can add them to the [`system_requirements.txt`](system_requirements.txt) file in the root of the node repository and redeploy the app.

```yaml
# workflows.yml
- name:
  custom_nodes:
    - url: https://github.com/ltdrdata/ComfyUI-Manager.git
      name: ComfyUI-Manager
      recursive: false # optional
      branch: main # optional
```

### Models

Follows the ComfyUI model directory format, if you need to add a new model type, you can do so by adding it to the `models` section.

The following configuration will download the SDXL model to `models/checkpoints/SDXL.safetensors`. Only the `url` and `name` fields are required. The `source` field is optional and is used to link to the model.

```yaml
# workflows.yml
- name: 
  models:
    checkpoints:
      - url: https://civitai.com/api/download/models/128078?type=Model&format=SafeTensor&size=pruned&fp=fp16
        name: SDXL.safetensors
        source: https://civitai.com/models/101055/sd-xl # optional
```

You can set the `HUGGINGFACE_TOKEN` and `CIVITAI_TOKEN` environment variables if you are using models from Hugging Face or Civitai. 

```bash
fly secrets set \
  HUGGINGFACE_TOKEN=... \
  CIVITAI_TOKEN=...
```

If you need additional authentication for a model, you will need to update the [`download-models.py`](download-models.py) script.