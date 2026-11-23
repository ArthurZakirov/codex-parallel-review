import importlib.util
from pathlib import Path


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
    assert "1 | pass" in batch["code"][0]
