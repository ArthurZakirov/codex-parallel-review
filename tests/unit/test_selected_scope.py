import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "src/parallel-review/skills/review-scope/scripts/review.py"
spec = importlib.util.spec_from_file_location("selected_review", SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def test_overlapping_paths_include_complete_nested_files_once(tmp_path):
    nested = tmp_path / "docs" / "deep"
    nested.mkdir(parents=True)
    doc = nested / "guide.md"
    doc.write_text("first\nlast\n")
    source = tmp_path / "service.py"
    source.write_text("pass")
    (nested / "linked.md").symlink_to(source)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/internal.md").touch()

    files = review.selected_files([tmp_path, nested, doc])
    assert files == sorted([doc, source])
    batch, = review.evidence_batches(files)
    assert "1 | first\n2 | last" in batch["markdown"][0]
    assert "1 | pass" in batch["python"][0]


@pytest.mark.parametrize("filenames", [("guide.MD",), ("service.py",), ("app.ts",),
                                       ("guide.MD", "service.py", "app.ts", "types.pyi")])
@pytest.mark.parametrize("workflow", ["manual", "hook"])
def test_each_reviewer_receives_only_its_file_type(tmp_path, monkeypatch, filenames, workflow):
    import patches
    import reviews

    paths = [tmp_path / name for name in filenames]
    for path in paths:
        path.write_text(path.name)

    jobs = {}
    def capture(job):
        role, evidence, _ = job
        assert role not in jobs
        jobs[role] = evidence
        return role

    monkeypatch.setattr(reviews, "_review", capture)

    if workflow == "manual":
        reviews.review_batches(review.evidence_batches(review.selected_files([tmp_path])), "selected files")
    else:
        sections = "".join(f"*** Add File: {name}\n+{name}\n" for name in filenames)
        groups = patches.review_inputs(dict(tool_name="apply_patch", tool_response="Exit code: 0",
                                            tool_input={"command": "*** Begin Patch\n" + sections + "*** End Patch"}))
        reviews.parallel_review(groups)

    expected = {"guide.MD": {"reader", "representation"},
                "app.ts": {"experience", "standards", "correctness"},
                "service.py": {"experience", "standards", "correctness", "module_ordering"}}
    expected["types.pyi"] = expected["service.py"]
    assert set(jobs) == set.union(*(expected[name] for name in filenames))
    for role, evidence in jobs.items():
        for name in filenames:
            assert (name in evidence) == (role in expected[name])
