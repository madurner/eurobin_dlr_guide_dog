# AGENTS.md

This repository contains a guide dog application with a FastAPI backend and Streamlit frontend, integrated with the Links & Nodes (LN) PCVP pipeline for object detection.

## Project Structure

```
application/
├── fast_api_backend/     # FastAPI backend server
├── streamlit_frontend/   # Streamlit frontend
├── mockup_pipeline/      # PCVP pipeline configuration (LN-based)
├── tests/                # Test suite
└── docs/                 # Sphinx documentation
```

## Quick Start

1. **Install Conan dependencies** (required for backend):
   ```bash
   conan install conanfile.txt --install-folder conan_env
   source conan_env/conanrun.sh
   ```

2. **Start backend server**:
   ```bash
   ./start_backend_server.sh
   ```
   Or manually:
   ```bash
   python3 application/fast_api_backend/app/main.py
   ```

3. **Start Streamlit frontend** (optional):
   ```bash
   streamlit run application/streamlit_frontend/run_streamlit.py
   ```

## Key Details

### PCVP Pipeline
- The backend integrates with a Links & Nodes PCVP pipeline (`pcvp_client_py/3.2.0@semsa/unstable`)
- Pipeline modules: `pcvp_manager`, `guide_dog2_pcvp`, plus optional `yolov7_pcvp`, `dense_pose_pcvp`, `m3t_refiner_cpp_pcvp`
- Pipeline is managed via `ln_manager` on configurable address (default `localhost:38641`)
- Configuration files are in `application/mockup_pipeline/detection_configs/`

### Authentication
- Backend uses API key authentication via `x-api-key` header
- Valid keys are defined in `application/fast_api_backend/app/auth.py` (currently: `my_debug_key`, `my_secret_key`, `my_secret_key_2`)
- Each API key maps to a specific LN manager address

### API Endpoints
- `POST /camera` - Register camera with intrinsics
- `GET /camera` - Get registered camera
- `PUT /camera/{name}` - Update camera intrinsics
- `POST /image` - Upload image for processing
- `GET /image` - Get uploaded image
- `DELETE /image` - Delete image
- `POST /pipeline` - Start PCVP pipeline
- `GET /pipeline` - Get pipeline status
- `DELETE /pipeline` - Stop pipeline
- `GET /detection` - Run detection on uploaded image

### Development Commands
- **Run tests**: `pytest application/tests/`
- **Lint**: `ruff check application/`
- **Format**: `black application/`
- **Sort imports**: `isort application/`
- **Type check**: `pytype application/` or `mypy application/`
- **Build docs**: `cd docs && make html`

### Conan Requirements (from `conanfile.txt`)
- `fastapi/0.128.0@pypi/stable`
- `pcvp_client_py/3.2.0@semsa/unstable`
- `opencv-python/4.9.0.80@pypi/stable`
- `uvicorn/0.35.0@pypi/stable`
- `links_and_nodes_python/[~2]@common/stable`

## Important Notes

- **Conan environment must be activated** before running the backend server (the `start_backend_server.sh` script handles this)
- The LN manager must be running for detection to work - the `LNRunner` class handles this via `cissy run`
- Pipeline requires image intrinsics (width, height, fx, fy) to be set via `/camera` endpoint before detection
- Detection result includes 6DOF pose, instance ID, and class name for each detected object
