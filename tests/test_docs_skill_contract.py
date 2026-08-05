import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = ("ingest", "query", "lint", "faq", "graph")
OPERATION_TITLES = {
    "ingest": "Ingest",
    "query": "Query",
    "lint": "Lint",
    "faq": "FAQ",
    "graph": "Graph",
}
ACTION_SKILLS = {
    operation: ROOT / "skills" / f"llm-wiki-{operation}" / "SKILL.md"
    for operation in OPERATIONS
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def prompt_section(operation: str) -> str:
    text = read(ROOT / "docs" / "PROMPTS.md")
    heading = f"## {OPERATION_TITLES[operation]} 提示詞"
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


def test_every_prompt_uses_the_titled_telemetry_wrapper() -> None:
    for operation in OPERATIONS:
        section = prompt_section(operation)
        start_command = f'python3 scripts/wiki-usage.py start {operation} --title "<title>"'
        finish_command = f'python3 scripts/wiki-usage.py finish {operation} --title "<title>"'
        assert start_command in section, operation
        assert finish_command in section, operation
        assert section.index(start_command) < section.index(finish_command), operation


def test_lint_measurement_starts_before_automatic_lint() -> None:
    section = prompt_section("lint")
    assert section.index("wiki-usage.py start lint") < section.index("scripts/wiki-lint.py")


def test_ingest_has_thirteen_business_steps_and_external_telemetry() -> None:
    prompt = prompt_section("ingest")
    assert re.findall(r"(?m)^(\d+)\. ", prompt) == [str(number) for number in range(14)]
    assert "1–13 為 13 個業務步驟" in prompt
    assert "步驟 0 是寫入前的資料治理 gate" in prompt
    assert "telemetry wrapper，兩者皆不計入 13 步" in prompt

    agents = read(ROOT / "AGENTS.md")
    start = agents.index("# 🛠 操作：Ingest")
    end = agents.index("\n# ❓ 操作：Query", start)
    ingest_contract = agents[start:end]
    assert re.findall(r"(?m)^(\d+)\. ", ingest_contract) == [str(number) for number in range(1, 14)]
    assert "13 個 Ingest 業務步驟" in ingest_contract


def test_action_skills_remain_thin_delegators() -> None:
    for operation, path in ACTION_SKILLS.items():
        text = read(path)
        assert len(text.splitlines()) <= 24, path
        assert "AGENTS.md" in text, path
        assert "docs/PROMPTS.md" in text, path
        assert f"## {OPERATION_TITLES[operation]} 提示詞" in text, path
        assert "共用 telemetry wrapper" in text, path
        assert "scripts/wiki-usage.py" not in text, path


def test_contract_docs_do_not_use_untitled_finish_commands() -> None:
    paths = [
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        ROOT / "docs" / "PROMPTS.md",
        ROOT / "docs" / "skill-usage.md",
        ROOT / "skills" / "llm-wiki-example" / "SKILL.md",
    ]
    operation_pattern = "|".join((*OPERATIONS, re.escape("<operation>")))
    untitled = re.compile(
        rf"python3 scripts/wiki-usage\.py finish (?:{operation_pattern})(?! --title)"
    )
    for path in paths:
        assert not untitled.search(read(path)), path
