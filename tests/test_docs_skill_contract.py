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

#: How docs must invoke a repository script.  A bare ``python3`` is not
#: portable: Windows installs ``python.exe`` only, so the documented steps
#: would fail there for anyone following them literally.
RUN = "uv run python"


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
        start_command = f'{RUN} scripts/wiki-usage.py start {operation} --title "<title>"'
        finish_command = f'{RUN} scripts/wiki-usage.py finish {operation} --title "<title>"'
        assert start_command in section, operation
        assert finish_command in section, operation
        assert section.index(start_command) < section.index(finish_command), operation


def test_lint_measurement_starts_before_automatic_lint() -> None:
    section = prompt_section("lint")
    assert section.index("wiki-usage.py start lint") < section.index("scripts/wiki-lint.py")


def test_ingest_has_numbered_business_steps_and_external_telemetry() -> None:
    prompt = prompt_section("ingest")
    assert re.findall(r"(?m)^(\d+)\. ", prompt) == [str(number) for number in range(17)]
    assert "步驟 0 為資料治理 gate" in prompt
    assert "telemetry wrapper 不計入業務步驟" in prompt
    assert "兩段式" in prompt
    assert "ingest-cache.py" in prompt

    agents = read(ROOT / "AGENTS.md")
    start = agents.index("# 🛠 操作：Ingest")
    end = agents.index("\n# ❓ 操作：Query", start)
    ingest_contract = agents[start:end]
    assert re.findall(r"(?m)^(\d+)\. ", ingest_contract) == [
        str(number) for number in range(1, 17)
    ]
    assert "兩段式" in ingest_contract
    assert "ingest-cache.py" in ingest_contract


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
        rf"{re.escape(RUN)} scripts/wiki-usage\.py finish (?:{operation_pattern})(?! --title)"
    )
    for path in paths:
        assert not untitled.search(read(path)), path


#: Files whose commands a reader or Agent is expected to run.  ``wiki/`` is
#: excluded: its pages are knowledge content, and the one command block there
#: is a dated record of what a past lint run executed, not an instruction.
def _instruction_files() -> list[Path]:
    paths = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "SKILL.md"]
    paths += sorted((ROOT / "docs").rglob("*.md"))
    paths += sorted((ROOT / "skills").rglob("*.md"))
    paths += sorted((ROOT / "ops").glob("*.md"))
    paths += sorted((ROOT / ".github").rglob("*.yml"))
    paths += sorted((ROOT / "scripts").glob("*.py"))
    return [path for path in paths if path.is_file()]


def test_documented_commands_run_on_windows() -> None:
    """No documented command may invoke a bare ``python3``.

    Windows installs ``python.exe`` with no ``python3`` alias, and uv's venv
    does not create one either, so ``python3 ...`` and ``uv run ... python3``
    both fail there.  Shebang lines are exempt; they are never typed.
    """
    invocation = re.compile(r"python3\s+(?:-m\s|scripts/)")
    offenders = []
    for path in _instruction_files():
        for number, line in enumerate(read(path).splitlines(), 1):
            if line.startswith("#!"):
                continue
            if invocation.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    assert not offenders, "use `uv run python` instead:\n" + "\n".join(offenders)


#: A backtick span naming a repository script.
_SCRIPT_SPAN = re.compile(r"`([^`]*?\b[a-z][a-z_-]*\.py\b[^`]*)`")
#: ...where the script is followed by a subcommand or flag, i.e. an invocation
#: rather than a bare mention of the file.
_HAS_ARGUMENTS = re.compile(r"\b[a-z][a-z_-]*\.py\b\s+\S")


def test_documented_commands_are_runnable_as_written() -> None:
    """Any script shown with arguments must carry its `uv run` prefix.

    The same step is written out in AGENTS.md, docs/PROMPTS.md and
    docs/ingest-pipeline.md, and the copies had already drifted: two of them
    said ``ingest-cache.py record --sha256 …`` with no interpreter and no
    ``scripts/`` path, so an Agent following them literally got "command not
    found". Naming a script without arguments stays allowed — that is a
    reference, not an instruction.
    """
    offenders = []
    for path in _instruction_files():
        if path.suffix != ".md":
            continue
        for number, line in enumerate(read(path).splitlines(), 1):
            for span in _SCRIPT_SPAN.findall(line):
                if _HAS_ARGUMENTS.search(span) and "uv run" not in span:
                    offenders.append(f"{path.relative_to(ROOT)}:{number}: {span}")
    assert not offenders, "prefix with `uv run python`:\n" + "\n".join(offenders)


def test_the_three_ingest_step_lists_stay_in_step() -> None:
    """AGENTS, PROMPTS and the pipeline table enumerate the same steps.

    Three copies of one 17-step list is a maintenance hazard: inserting a
    step means renumbering all three. They are kept because each serves a
    different reader — the contract, the copy-paste prompt, and the
    cross-walk to the legacy 8/10-step models — so this pins the numbering
    they share instead. AGENTS omits step 0, the governance gate, which is
    stated as a precondition there rather than as a step.
    """
    prompt_steps = [int(n) for n in re.findall(r"(?m)^(\d+)\. ", prompt_section("ingest"))]

    agents = read(ROOT / "AGENTS.md")
    start = agents.index("# 🛠 操作：Ingest")
    end = agents.index("\n# ❓ 操作：Query", start)
    agents_steps = [int(n) for n in re.findall(r"(?m)^(\d+)\. ", agents[start:end])]

    pipeline = read(ROOT / "docs" / "ingest-pipeline.md")
    table_steps = [int(m) for m in re.findall(r"\|\s*\*\*(\d+)\*\*\s*\|", pipeline)]

    assert prompt_steps == list(range(17))
    assert agents_steps == list(range(1, 17))
    assert table_steps == list(range(17)), "pipeline table drifted from the step list"


def test_bundle_boundary_contract_has_no_legacy_operational_paths() -> None:
    paths = [ROOT / "AGENTS.md", ROOT / "README.md", *(ROOT / "docs").glob("*.md")]
    retired = ("wiki/purpose.md", "wiki/review/queue.md", "wiki/graph/insights.md")
    for path in paths:
        text = read(path)
        assert not any(value in text for value in retired), path
