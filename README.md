# envoy-cfg

> A CLI tool to manage and sync environment variable configs across multiple deployment targets with secret masking support.

---

## Installation

```bash
pip install envoy-cfg
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install envoy-cfg
```

---

## Usage

```bash
# Initialize a new config environment
envoy-cfg init

# Add or update a variable
envoy-cfg set DATABASE_URL "postgres://localhost:5432/mydb"

# Sync config to a deployment target
envoy-cfg sync --target production

# List all variables (secrets masked by default)
envoy-cfg list

# Show a specific variable value
envoy-cfg get DATABASE_URL --reveal
```

**Example output:**

```
$ envoy-cfg list
DATABASE_URL   = postgres://localhost:5432/mydb
API_SECRET_KEY = **********************
DEBUG          = false
```

Targets are defined in `.envoy-cfg.yaml` at the root of your project. Each target can map to a cloud provider, server group, or custom sync handler.

---

## Configuration

```yaml
# .envoy-cfg.yaml
targets:
  production:
    provider: aws-ssm
    path: /myapp/prod
  staging:
    provider: dotenv
    file: .env.staging
```

---

## License

This project is licensed under the [MIT License](LICENSE).