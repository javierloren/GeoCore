# Secrets and API Keys

GeoCore uses Roboflow for the current Core Box Vision prototype. API keys must
never be committed to GitHub.

## Local Development

Create a local file:

```text
.streamlit/secrets.toml
```

Use this structure:

```toml
ROBOFLOW_API_KEY = "your-private-key"
ROBOFLOW_DATASET_SLUG = "software-szwke"
ROBOFLOW_MODEL_VERSION = 3
ROBOFLOW_CONFIDENCE = 35
ROBOFLOW_OVERLAP = 30
```

`.streamlit/secrets.toml` is ignored by Git. Only
`.streamlit/secrets.toml.example` should be committed.

## Streamlit Community Cloud

In the Streamlit app settings, add the same values under the app's secrets
section. Do not put the API key in source code, README files, issues, commits, or
screenshots intended for public sharing.

## Rotation

If a private API key is accidentally shown in public, committed to Git, or shared
outside trusted private channels, revoke it in Roboflow and create a new one.

## Maintainer Rule

GeoCore source code should read secrets only from `st.secrets`, environment
variables, or local ignored files. It should never contain real private
credentials.
