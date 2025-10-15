# Research_And_Emerging_topics_Labs
Labs from a class I am taking at uni

## Setup Instructions

Each lab is a separate UV project. To work on a lab:

1. Navigate to the lab directory:
   ```bash
   cd Lab1  # or Lab2, Lab3, etc.
   ```

2. Sync dependencies:
   ```bash
   uv sync
   ```

3. Add ipykernel for Jupyter notebook support:
   ```bash
   uv add --dev ipykernel
   ```

4. Select the UV virtual environment as the kernel in your Jupyter notebook
