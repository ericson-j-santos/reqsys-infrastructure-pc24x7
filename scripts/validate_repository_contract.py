#!/usr/bin/env python3
"""Fail-closed validation for the PC24x7 repository ownership contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "pc24x7-dev-ownership.json"
README = ROOT / "README.md"
START = "<!-- PC24X7_CONTRACT_PATHS_START -->"
END = "<!-- PC24X7_CONTRACT_PATHS_END -->"


def fail(message: str) -> None:
    raise SystemExit(f"CONTRACT_INVALID: {message}")


def load_contract() -> dict:
    try:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot_read_contract: {exc}")
    if not isinstance(payload, dict):
        fail("root_not_object")
    return payload


def documented_paths(readme: str) -> list[str]:
    if START not in readme or END not in readme:
        fail("readme_contract_markers_missing")
    block = readme.split(START, 1)[1].split(END, 1)[0]
    paths: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if line.startswith("- `") and line.endswith("`"):
            paths.append(line[3:-1])
    if not paths:
        fail("readme_contract_paths_empty")
    return paths


def validate() -> dict:
    contract = load_contract()

    if contract.get("environment") != "dev":
        fail("environment_must_be_dev")

    owner = contract.get("runtime_owner") or {}
    if owner.get("repository") != "ericson-j-santos/reqsys-v2-enterprise-real":
        fail("unexpected_runtime_owner")
    if owner.get("branch") != "main":
        fail("runtime_owner_branch_must_be_main")
    if owner.get("operating_model") != "windows_scheduled_task":
        fail("operating_model_must_match_current_pc24x7")
    if owner.get("task_name") != "ReqSys-Dev-Runtime-Supervisor":
        fail("unexpected_runtime_task")

    controls = contract.get("required_upstream_controls") or {}
    if controls.get("exact_expected_sha_required") is not True:
        fail("exact_expected_sha_required")
    if controls.get("reuse_evidence_from_other_sha_allowed") is not False:
        fail("cross_sha_evidence_must_be_forbidden")
    required_health = {
        "/api/health",
        "/api/runtime/health",
        "/api/runtime/build-info",
    }
    if set(controls.get("health_paths") or []) != required_health:
        fail("health_contract_incomplete")

    scope = contract.get("scope") or {}
    if scope.get("hml_deploy_automated_here") is not False:
        fail("hml_must_remain_out_of_scope")
    if scope.get("prod_deploy_automated_here") is not False:
        fail("prod_must_remain_out_of_scope")
    if scope.get("deploy_executed_by_this_contract_ci") is not False:
        fail("contract_ci_must_not_deploy")

    local_paths = contract.get("local_contract_paths") or []
    if not local_paths:
        fail("local_contract_paths_empty")
    missing = sorted(path for path in local_paths if not (ROOT / path).is_file())
    if missing:
        fail("missing_local_paths=" + ",".join(missing))

    readme = README.read_text(encoding="utf-8")
    declared = documented_paths(readme)
    if declared != local_paths:
        fail(
            "readme_paths_drift="
            + json.dumps({"expected": local_paths, "observed": declared}, ensure_ascii=False)
        )

    result = {
        "status": "passed",
        "environment": "dev",
        "runtime_owner": owner["repository"],
        "local_paths_checked": len(local_paths),
        "exact_expected_sha_required": True,
        "hml_prod_touched": False,
        "deploy_executed": False,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return result


if __name__ == "__main__":
    try:
        validate()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"CONTRACT_INVALID: unexpected_error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
