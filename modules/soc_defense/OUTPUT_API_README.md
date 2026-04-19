# SOC Output API

This API exposes SOC output artifacts for external dashboards or projects.

## Run

```bash
uvicorn modules.soc_defense.api:app --host 0.0.0.0 --port 8001
```

## Endpoints

- `GET /`
  - Health check.

- `GET /api/v1/soc/outputs`
  - Returns recent SOC outputs.
  - Query params:
    - `limit`
    - `component`

- `GET /api/v1/soc/outputs/latest`
  - Returns the newest SOC output.
  - Optional query param:
    - `component`

- `GET /api/v1/soc/outputs/{file_name}`
  - Returns one specific output JSON file.

## Example

```text
http://<soc-ip>:8001/api/v1/soc/outputs/latest
```

This is the endpoint another project should call to pull SOC output from your project.
