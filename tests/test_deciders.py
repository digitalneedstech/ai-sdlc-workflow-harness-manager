"""Model decider tests. No network."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from pipeline_orchestrator.deciders.base import Decision, DecisionError, DecisionRequest
from pipeline_orchestrator.deciders.factory import make_decider
from pipeline_orchestrator.deciders.fixed import FixedDecider
from pipeline_orchestrator.deciders.jev import JevAnswer, JevDecider, JevUnavailable
from pipeline_orchestrator.deciders.settings import DEFAULT_CANDIDATES, OrchestratorSettings, load_settings
from pipeline_orchestrator.engine import advance, start_run
from pipeline_orchestrator.graph import feature_development
from pipeline_orchestrator.runners.cursor_sdk import catalog_ids
from pipeline_orchestrator.runners.fake import FakeRunner

CATALOG = ("composer-2.5", "gpt-5.4-medium", "auto")


def _request(step_id: str, pin: str = "") -> DecisionRequest:
    return DecisionRequest(
        step_id=step_id,
        job="Writes the product requirements." if step_id.startswith("product") else "Implements the change.",
        user_request="redesign checkout",
        workflow="feature-development",
        change_class="feature",
        prior_status="",
        catalog=CATALOG,
        pin=pin,
    )


def _settings(**overrides: object) -> OrchestratorSettings:
    settings = OrchestratorSettings()
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


class ScriptClient:
    def __init__(self, by_step: dict[str, JevAnswer | Exception]) -> None:
        self.by_step = by_step
        self.calls: list[str] = []

    def choose(self, *, state: dict, options: dict[str, str | None], model: str) -> JevAnswer:
        step = str(state["agent"])
        self.calls.append(step)
        planned = self.by_step[step]
        if isinstance(planned, Exception):
            raise planned
        return planned


def test_factory_selects_fixed_or_jev(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    (app / ".pipeline" / "config.json").write_text(
        json.dumps({"orchestrator": {"decider": "fixed"}}) + "\n",
        encoding="utf-8",
    )
    assert make_decider(app).name == "fixed"
    (app / ".pipeline" / "config.json").write_text(
        json.dumps({"orchestrator": {"decider": "jev"}}) + "\n",
        encoding="utf-8",
    )
    assert make_decider(app).name == "jev"


def test_unknown_decider_names_the_known_ones(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    (app / ".pipeline" / "config.json").write_text(
        json.dumps({"orchestrator": {"decider": "oracle"}}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="known: fixed, jev"):
        make_decider(app)


def test_fixed_uses_fallback_then_pin_then_step():
    decider = FixedDecider(_settings())
    fallback = decider.decide(_request("developer-agent"))
    assert fallback.model == "composer-2.5"
    assert fallback.reason == "fixed"
    assert fallback.decider == "fixed"

    pinned = decider.decide(_request("developer-agent", pin="gpt-5.4-medium"))
    assert pinned.model == "gpt-5.4-medium"
    assert pinned.reason == "pin"

    configured = FixedDecider(_settings(steps={"product-manager-agent": "auto"}))
    choice = configured.decide(_request("product-manager-agent"))
    assert choice.model == "auto"
    assert choice.reason == "config"


def test_pin_missing_from_catalog_fails():
    decider = FixedDecider(_settings())
    with pytest.raises(DecisionError, match="not in the catalog"):
        decider.decide(_request("developer-agent", pin="missing-model"))


def test_jev_confident_choice_and_distinct_agents():
    client = ScriptClient(
        {
            "product-manager-agent": JevAnswer(
                choice="gpt-5.4-medium",
                confidence=0.91,
                probabilities={"gpt-5.4-medium": 0.91, "composer-2.5": 0.09},
                jev_model="jev-1.13.0",
            ),
            "developer-agent": JevAnswer(
                choice="composer-2.5",
                confidence=0.8,
                probabilities={"composer-2.5": 0.8, "gpt-5.4-medium": 0.2},
                jev_model="jev-1.13.0",
            ),
        }
    )
    decider = JevDecider(_settings(), client=client)
    pm = decider.decide(_request("product-manager-agent"))
    dev = decider.decide(_request("developer-agent"))
    assert pm.model == "gpt-5.4-medium"
    assert pm.reason == "jev"
    assert pm.decider == "jev"
    assert pm.confidence == 0.91
    assert dev.model == "composer-2.5"
    assert dev.reason == "jev"
    assert client.calls == ["product-manager-agent", "developer-agent"]


def test_jev_sends_cursor_description_for_each_model():
    captured: dict = {}

    class Capture:
        def choose(self, *, state, options, model):
            captured["options"] = options
            captured["capability"] = state["capability"]
            return JevAnswer(
                choice="gpt-5.4-medium",
                confidence=0.9,
                probabilities={"gpt-5.4-medium": 0.9, "composer-2.5": 0.1},
                jev_model="jev-1.13.0",
            )

    request = DecisionRequest(
        step_id="product-manager-agent",
        job="Writes the product requirements.",
        user_request="redesign checkout",
        workflow="feature-development",
        change_class="feature",
        prior_status="",
        catalog=("composer-2.5", "gpt-5.4-medium"),
        model_info={
            "gpt-5.4-medium": {
                "display_name": "GPT 5.4",
                "description": "Strong reasoning for planning and review.",
                "variants": [{"display_name": "High", "description": "More thinking", "is_default": True}],
            },
            "composer-2.5": {
                "display_name": "Composer 2.5",
                "description": "Fast coding model for edits.",
            },
        },
    )
    decision = JevDecider(_settings(), client=Capture()).decide(request)
    assert decision.model == "gpt-5.4-medium"
    assert "planning" in captured["capability"]
    gpt = captured["options"]["gpt-5.4-medium"]
    assert gpt["display_name"] == "GPT 5.4"
    assert gpt["description"] == "Strong reasoning for planning and review."
    assert gpt["variants"][0]["display_name"] == "High"
    assert "reasoning" in gpt["fit"].lower()
    assert captured["options"]["composer-2.5"]["description"] == "Fast coding model for edits."
    assert "Poor fit" in captured["options"]["composer-2.5"]["for_this_agent"]
    assert "Good fit" in captured["options"]["gpt-5.4-medium"]["for_this_agent"]


def test_jev_low_confidence_uses_fallback():
    client = ScriptClient(
        {
            "developer-agent": JevAnswer(
                choice="gpt-5.4-medium",
                confidence=0.2,
                probabilities={"gpt-5.4-medium": 0.4, "composer-2.5": 0.35, "auto": 0.25},
                jev_model="jev-1.13.0",
            )
        }
    )
    decision = JevDecider(_settings(), client=client).decide(_request("developer-agent"))
    assert decision.model == "composer-2.5"
    assert decision.reason == "low_confidence"
    assert decision.confidence == 0.2
    assert decision.jev_choice == "gpt-5.4-medium"
    assert decision.decider == "jev"
    text = decision.format("developer-agent")
    assert "jev_choice=gpt-5.4-medium" in text
    assert "need: implementation:" in text
    assert "basis: Jev picked gpt-5.4-medium (0.40). Confidence 0.20 is below the floor, so fallback composer-2.5 runs." in text
    assert "scores: gpt-5.4-medium 0.40; composer-2.5 0.35; auto 0.25" in text
    assert "display_name:" not in text
    assert "variants:" not in text
    assert decision.summary_line("developer-agent") == (
        "  developer-agent  chosen=composer-2.5  reason=low_confidence  "
        "jev=gpt-5.4-medium  confidence=0.20"
    )


def test_format_keeps_only_top_scores():
    decision = Decision(
        model="composer-2.5",
        reason="jev",
        decider="jev",
        fallback="composer-2.5",
        confidence=0.9,
        probabilities={
            "composer-2.5": 0.50,
            "gpt-5.4-medium": 0.20,
            "auto": 0.10,
            "grok-4.6": 0.08,
            "gemini-3-flash": 0.07,
            "muse-spark-1.3": 0.05,
        },
        capability="implementation: edit code and fix defects.",
        criteria={"composer-2.5": {"display_name": "Composer 2.5", "fit": "Fast coding model."}},
    )
    text = decision.format("developer-agent")
    assert "basis: Jev picked composer-2.5 (0.50). That model runs." in text
    assert "scores: composer-2.5 0.50; gpt-5.4-medium 0.20; auto 0.10; grok-4.6 0.08; gemini-3-flash 0.07 (+1)" in text
    assert "muse-spark-1.3" not in text
    assert "display_name:" not in text


def test_jev_sends_only_candidate_models():
    captured: dict = {}

    class Capture:
        def choose(self, *, state, options, model):
            captured["options"] = options
            return JevAnswer(
                choice="claude-opus-5",
                confidence=0.9,
                probabilities={"claude-opus-5": 0.9, "composer-2.5": 0.1},
                jev_model="jev-1.13.0",
            )

    request = DecisionRequest(
        step_id="product-manager-agent",
        job="Writes the product requirements.",
        user_request="redesign checkout",
        workflow="feature-development",
        change_class="feature",
        prior_status="",
        catalog=(
            "composer-2.5",
            "composer-2",
            "grok-4.6",
            "claude-opus-5",
            "gpt-5.5",
            "muse-spark-1.3",
            "gemini-3-flash",
        ),
        model_info={"claude-opus-5": {"display_name": "Claude Opus 5"}},
    )
    decision = JevDecider(
        _settings(candidates=DEFAULT_CANDIDATES),
        client=Capture(),
    ).decide(request)
    assert decision.model == "claude-opus-5"
    assert set(captured["options"]) == {"composer-2.5", "grok-4.6", "claude-opus-5", "gpt-5.5"}
    assert "muse-spark-1.3" not in captured["options"]
    assert "Poor fit" in captured["options"]["composer-2.5"]["for_this_agent"]
    assert "Good fit" in captured["options"]["claude-opus-5"]["for_this_agent"]
    assert "sent: composer-2.5, grok-4.6, claude-opus-5, gpt-5.5" in decision.format(
        "product-manager-agent"
    )


def test_empty_candidates_sends_full_catalog():
    captured: dict = {}

    class Capture:
        def choose(self, *, state, options, model):
            captured["ids"] = list(options)
            return JevAnswer(choice="composer-2.5", confidence=0.9, probabilities={"composer-2.5": 0.9})

    request = DecisionRequest(
        step_id="developer-agent",
        job="Implements the change.",
        user_request="add a line",
        workflow="feature-development",
        change_class="micro",
        prior_status="",
        catalog=("composer-2.5", "muse-spark-1.3", "gemini-3-flash"),
    )
    JevDecider(_settings(candidates=()), client=Capture()).decide(request)
    assert captured["ids"] == ["composer-2.5", "muse-spark-1.3", "gemini-3-flash"]


def test_load_settings_uses_default_candidates(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    (app / ".pipeline" / "config.json").write_text(
        json.dumps({"orchestrator": {"decider": "jev"}}) + "\n",
        encoding="utf-8",
    )
    assert load_settings(app).candidates == DEFAULT_CANDIDATES
    (app / ".pipeline" / "config.json").write_text(
        json.dumps({"orchestrator": {"models": {"candidates": []}}}) + "\n",
        encoding="utf-8",
    )
    assert load_settings(app).candidates == ()


def test_load_settings_reads_candidate_objects_and_cards(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    (app / ".pipeline" / "config.json").write_text(
        json.dumps(
            {
                "orchestrator": {
                    "models": {
                        "candidates": [
                            "composer-2.5",
                            {
                                "id": "glm-5.2",
                                "kind": "reasoning",
                                "fit": "Custom reasoning card.",
                                "display_name": "GLM 5.2",
                            },
                        ],
                        "cards": {
                            "composer-2.5": {"fit": "Override composer fit."},
                            "glm-5.2": {"description": "User-supplied description."},
                        },
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    settings = load_settings(app)
    assert settings.candidates == ("composer-2.5", "glm-5.2")
    assert settings.cards["glm-5.2"]["kind"] == "reasoning"
    assert settings.cards["glm-5.2"]["fit"] == "Custom reasoning card."
    assert settings.cards["glm-5.2"]["display_name"] == "GLM 5.2"
    assert settings.cards["glm-5.2"]["description"] == "User-supplied description."
    assert settings.cards["composer-2.5"]["fit"] == "Override composer fit."


def test_user_card_overrides_fit_and_kind():
    captured: dict = {}

    class Capture:
        def choose(self, *, state, options, model):
            captured["options"] = options
            return JevAnswer(
                choice="glm-5.2",
                confidence=0.9,
                probabilities={"glm-5.2": 0.9, "composer-2.5": 0.1},
                jev_model="jev-1.13.0",
            )

    request = DecisionRequest(
        step_id="product-manager-agent",
        job="Writes the product requirements.",
        user_request="redesign checkout",
        workflow="feature-development",
        change_class="feature",
        prior_status="",
        catalog=("composer-2.5", "glm-5.2"),
    )
    decision = JevDecider(
        _settings(
            candidates=("composer-2.5", "glm-5.2"),
            cards={
                "glm-5.2": {
                    "kind": "reasoning",
                    "fit": "Custom reasoning card.",
                    "display_name": "GLM 5.2",
                }
            },
        ),
        client=Capture(),
    ).decide(request)
    assert decision.model == "glm-5.2"
    glm = captured["options"]["glm-5.2"]
    assert glm["fit"] == "Custom reasoning card."
    assert glm["display_name"] == "GLM 5.2"
    assert "Good fit" in glm["for_this_agent"]


def test_jev_missing_key_uses_fallback(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    decision = JevDecider(_settings()).decide(_request("developer-agent"))
    assert decision.reason == "jev_unavailable"
    assert decision.model == "composer-2.5"
    assert decision.decider == "jev"


def test_jev_client_error_uses_fallback():
    client = ScriptClient({"developer-agent": JevUnavailable("timeout")})
    decision = JevDecider(_settings(), client=client).decide(_request("developer-agent"))
    assert decision.reason == "jev_unavailable"
    assert decision.model == "composer-2.5"


def test_jev_pin_skips_the_client():
    client = ScriptClient({})
    decision = JevDecider(_settings(), client=client).decide(
        _request("developer-agent", pin="gpt-5.4-medium")
    )
    assert decision.reason == "pin"
    assert decision.model == "gpt-5.4-medium"
    assert decision.decider == "jev"
    assert client.calls == []


def test_catalog_ids_accepts_strings_and_objects():
    assert catalog_ids(["composer-2.5", "auto"]) == ["composer-2.5", "auto"]
    assert catalog_ids({"models": [{"id": "composer-2.5"}, {"name": "auto"}]}) == [
        "composer-2.5",
        "auto",
    ]


def test_empty_catalog_is_startup_failure(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    spec = feature_development()
    run = start_run(
        project=app,
        spec=spec,
        slug="empty-catalog",
        change_class="micro",
        runner_name="fake",
        kit_version="test",
    )
    code = asyncio.run(
        advance(project=app, spec=spec, run=run, runner=FakeRunner(catalog=[]))
    )
    assert code == 1


def test_rejected_model_retries_fallback_without_critic_retry(tmp_path: Path):
    class Script:
        name = "script"

        def decide(self, request: DecisionRequest) -> Decision:
            return Decision(
                model="gpt-5.4-medium",
                reason="jev",
                decider="script",
                fallback="composer-2.5",
            )

    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    spec = feature_development()
    run = start_run(
        project=app,
        spec=spec,
        slug="reject-model",
        change_class="micro",
        runner_name="fake",
        kit_version="test",
    )
    runner = FakeRunner({"developer-agent": {"reject_model": "gpt-5.4-medium"}})
    code = asyncio.run(
        advance(project=app, spec=spec, run=run, runner=runner, decider=Script())
    )
    assert code == 0
    saved = json.loads(
        (app / ".pipeline" / "state" / "runs" / "reject-model.json").read_text(encoding="utf-8")
    )
    routing = saved["steps"]["developer-agent"]["routing"]
    assert routing["cursor_rejected"] == "gpt-5.4-medium"
    assert saved["steps"]["developer-agent"]["model"] == "composer-2.5"
    assert not saved.get("retries")
