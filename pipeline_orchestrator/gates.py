"""Human sign-off gates."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pipeline_orchestrator.events import emit
from pipeline_orchestrator.state import load_run, save_run, signoff_path


def approve(*, project: Path, slug: str, gate: str, note: str = "none") -> int:
    run = load_run(project, slug)
    gates = run.setdefault("gates", {})
    gates.setdefault(gate, {})
    today = date.today().isoformat()
    gates[gate]["status"] = "approved"
    gates[gate]["approved_at"] = today
    gates[gate]["note"] = note or "none"
    artifacts = {
        "requirements": "prd.md",
        "architect": "architecture.md",
        "ba": "HANDOFF.md",
    }
    artifact = artifacts.get(gate, "")
    label = note or "none"
    body = "# Sign-off -- %s\n\n" % gate
    body += "**SIGNOFF:** approved\nSIGNOFF: approved\n"
    body += "**role:** %s\n" % gate
    body += "**slug:** %s\n" % slug
    body += "**artifact:** features/%s/%s\n" % (slug, artifact)
    body += "**concerns_reviewed:** none\n"
    body += "**approved_at:** %s\n" % today
    body += "**note:** %s\n" % label
    path = signoff_path(project, slug, gate)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    save_run(project, run)
    emit(project, "gate_approved", slug=slug, gate=gate)
    print("approved gate=%s slug=%s" % (gate, slug))
    return 0
