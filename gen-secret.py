from pathlib import Path
import secrets

env_path = Path(".env")
key = "SECRET_KEY"

content = env_path.read_text().splitlines() if env_path.exists() else []

if any(line.startswith(f"{key}=") for line in content):
    print("SECRET_KEY sudah ada, skip")
else:
    value = secrets.token_hex(64)
    content.insert(0, f"{key}={value}")
    env_path.write_text("\n".join(content) + "\n")
    print("SECRET_KEY ditambahkan di baris pertama")
