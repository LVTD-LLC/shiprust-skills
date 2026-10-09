#!/usr/bin/env python3
"""Credential-safe, dependency-free ShipRust REST fallback. Python 3.10+."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
from uuid import UUID

ORIGIN = "https://shiprust.com"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def project_id(value):
    return str(UUID(value))


def request(method, path, payload=None, authenticated=True):
    # Endpoint choices are internal constants, never caller-controlled origins.
    if not path.startswith("/api/v1/") or ".." in path or "?" in path:
        raise ValueError("Invalid API path")
    headers = {"Accept": "application/json", "User-Agent": "shiprust-skills/1.0.0"}
    if authenticated:
        key = os.environ.get("SHIPRUST_API_KEY", "").strip()
        if not key or not key.startswith("sr_") or any(c.isspace() for c in key):
            raise ValueError("Set SHIPRUST_API_KEY in the protected runtime environment.")
        headers["Authorization"] = "Bearer " + key
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(ORIGIN + path, data=data, headers=headers, method=method)
    return urllib.request.build_opener(NoRedirect()).open(req, timeout=60)


def run(args):
    command = args.command
    payload = None
    method = "GET"
    path = {"account": "/api/v1/me", "options": "/api/v1/options", "projects": "/api/v1/projects", "create": "/api/v1/projects"}.get(command)
    if command in ("project", "download", "delete"):
        path = "/api/v1/projects/" + project_id(args.id)
    if command == "create":
        payload = json.loads(args.file.read_text())
        if not isinstance(payload, dict):
            raise ValueError("Project request must be a JSON object")
        method = "POST"
    if command == "delete":
        if not args.confirm_delete:
            raise ValueError("Deletion requires --confirm-delete and the user's authorization")
        method = "DELETE"
    if command == "download":
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("Output already exists; refusing to overwrite")
        path += "/download"
    with request(method, path, payload, authenticated=command != "options") as response:
        if command == "download":
            if "application/zip" not in response.headers.get("Content-Type", ""):
                raise ValueError("Expected a ZIP response; no file saved")
            # No overwrite even if another process created the file during the request.
            try:
                with args.output.open("xb") as out:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)
            except FileExistsError:
                raise ValueError("Output already exists; refusing to overwrite") from None
            print(f"Downloaded {args.output}. Inspect entries before extracting into an empty directory.")
        elif response.status == 204:
            print("Project deleted.")
        else:
            print(json.dumps(json.load(response), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("account", "options", "projects"):
        commands.add_parser(name)
    create = commands.add_parser("create")
    create.add_argument("--file", type=Path, required=True)
    for name in ("project", "download", "delete"):
        sub = commands.add_parser(name)
        sub.add_argument("id", help="Project UUID")
        if name == "download":
            sub.add_argument("--output", type=Path, required=True)
        if name == "delete":
            sub.add_argument("--confirm-delete", action="store_true")
    try:
        run(parser.parse_args())
    except urllib.error.HTTPError as e:
        # Never dump request headers, credentials or remote response bodies.
        print(f"ShipRust HTTP {e.code}. See references/api.md for recovery. No automatic retry.", file=sys.stderr)
        return 1
    except (ValueError, OSError, urllib.error.URLError) as e:
        # Error strings may come from libraries; redact the runtime key defensively.
        message = str(e)
        key = os.environ.get("SHIPRUST_API_KEY")
        if key:
            message = message.replace(key, "[redacted]")
        print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
