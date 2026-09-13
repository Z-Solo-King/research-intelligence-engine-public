from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PUBLIC_FILES = {
    "INSTALL.ps1",
    "README.txt",
    "README_BATCH.txt",
    "PHASE_0_CONSOLIDATION_AUDIT.md",
}


def test_private_bundle_files_are_absent():
    for name in FORBIDDEN_PUBLIC_FILES:
        assert not (ROOT / name).exists(), f"private/internal file leaked: {name}"


def test_public_deployment_uses_safe_placeholders():
    text = (ROOT / "wrangler.toml").read_text(encoding="utf-8")
    assert "REPLACE_WITH_PRIVATE_CONTROL_PLANE_SERVICE" in text
    assert "REPLACE_WITH_D1_DATABASE_ID" in text
    assert "REPLACE_WITH_PUBLIC_DATABASE_NAME" in text
    assert "B2_BUCKET = \"SoloKing\"" in text
    assert "B2_ENDPOINT = \"https://s3.eu-central-003.backblazeb2.com\"" in text
    assert "[[r2_buckets]]" not in text
    assert "ARTIFACTS" not in text
    assert "research-intelligence-engine-private" not in text


def test_public_docs_do_not_name_private_service():
    for path in (ROOT / "README.md", ROOT / "DEPLOYMENT.md"):
        text = path.read_text(encoding="utf-8")
        assert "research-intelligence-engine-private" not in text
