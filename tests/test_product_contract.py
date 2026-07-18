from __future__ import annotations

import re
import subprocess
import sys
import unittest
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_URL = "https://monarchcastletech.github.io/Cloudy-Shiny/"
PRODUCT_TITLE = "Cloudy&Shiny Index"
DOCUMENT_TITLE = f"{PRODUCT_TITLE} | Monarch Castle Technologies"


class ProductContractTests(unittest.TestCase):
    def test_dependencies_have_one_canonical_declaration(self) -> None:
        declarations = sorted(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("requirements.txt")
            if ".git" not in path.parts
        )
        self.assertEqual(declarations, ["requirements.txt"])

        names: list[str] = []
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
            declaration = line.split("#", 1)[0].strip()
            if not declaration:
                continue
            name = re.split(r"[<>=!~;\[]", declaration, maxsplit=1)[0]
            names.append(name.lower().replace("_", "-"))
        self.assertEqual(len(names), len(set(names)), "duplicate root dependencies")

    def test_titles_and_canonical_url_are_consistent(self) -> None:
        template = (ROOT / "template.html").read_text(encoding="utf-8")
        generated = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for surface in (template, generated):
            self.assertEqual(
                re.findall(r"<title>(.*?)</title>", surface, flags=re.IGNORECASE),
                [DOCUMENT_TITLE],
            )
            self.assertEqual(
                re.findall(
                    r'<link rel="canonical" href="([^"]+)">',
                    surface,
                    flags=re.IGNORECASE,
                ),
                [CANONICAL_URL],
            )
            self.assertEqual(
                re.findall(
                    r'<meta property="og:url" content="([^"]+)">',
                    surface,
                    flags=re.IGNORECASE,
                ),
                [CANONICAL_URL],
            )
        self.assertIn(f'page_title="{PRODUCT_TITLE}"', app)
        self.assertIn('"{UPDATED_ISO}": updated_iso', app)
        self.assertIn(f"# {PRODUCT_TITLE}", readme)
        self.assertIn(f"[Open the published project]({CANONICAL_URL})", readme)
        self.assertNotIn("monarchcastle.tech/Cloudy-Shiny", readme)

    def test_endorsement_and_approved_logo_are_visible(self) -> None:
        logo = ROOT / "logo.png"
        self.assertTrue(logo.is_file())
        self.assertGreater(logo.stat().st_size, 100)

        for filename in ("template.html", "index.html"):
            surface = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("Part of Monarch Castle Technologies", surface)
            self.assertRegex(
                surface,
                r'<img src="logo\.png" alt="Cloudy&amp;Shiny Index logo"',
            )

    def test_methodology_and_freshness_are_explicit(self) -> None:
        for filename in ("template.html", "index.html"):
            surface = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn('<section id="methodology"', surface)
            self.assertIn("Methodology and Weights", surface)
            self.assertIn("<strong>Freshness:</strong> Latest published reading", surface)
            self.assertIn("Updates approximately every 50 minutes", surface)
            self.assertRegex(
                surface,
                r'<time[^>]+datetime="[^"]+"[^>]*>[^<]+UTC</time>',
            )

    def test_canonical_surface_uses_approved_tokens_and_accessibility_basics(self) -> None:
        template = (ROOT / "template.html").read_text(encoding="utf-8")
        for token in (
            "--bg:#15130f",
            "--panel:#191711",
            "--card:#17140f",
            "--border:#2c2820",
            "--accent:#c9a24b",
            "--txt:#ece6d8",
            "--muted:#9a9284",
            '"IBM Plex Sans"',
            '"IBM Plex Mono"',
            '"Spectral"',
        ):
            self.assertIn(token, template)

        for requirement in (
            'class="skip-link"',
            'id="main-content"',
            ":focus-visible",
            "prefers-reduced-motion",
            'aria-live="polite"',
            "@media (max-width:640px)",
        ):
            self.assertIn(requirement, template)

        generated = (ROOT / "index.html").read_text(encoding="utf-8")
        h1_text = [
            unescape(re.sub(r"<[^>]+>", "", value)).strip()
            for value in re.findall(r"<h1\b[^>]*>(.*?)</h1>", generated, re.DOTALL)
        ]
        self.assertEqual(h1_text, [PRODUCT_TITLE])

        h2_ids = re.findall(r'<h2\b[^>]*id="([^"]+)"[^>]*>', generated)
        self.assertEqual(
            h2_ids,
            [
                "sentiment-panel-title",
                "performance-panel-title",
                "reliability-panel-title",
            ],
        )
        for heading_id in h2_ids:
            self.assertIn(f'aria-labelledby="{heading_id}"', generated)
        self.assertGreaterEqual(len(re.findall(r"<h3\b", generated)), 4)

    def test_generated_surface_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "build_index.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Static dashboard is current", result.stdout)

    def test_hourly_workflow_preserves_cadence_and_has_safe_dry_run(self) -> None:
        workflow = (ROOT / ".github/workflows/hourly.yml").read_text(encoding="utf-8")
        expected_crons = (
            "0 0,5,10,15,20 * * *",
            "50 0,5,10,15,20 * * *",
            "40 1,6,11,16,21 * * *",
            "30 2,7,12,17,22 * * *",
            "20 3,8,13,18,23 * * *",
            "10 4,9,14,19 * * *",
        )
        self.assertEqual(
            re.findall(r"- cron: '([^']+)'", workflow),
            list(expected_crons),
        )
        self.assertIn("dry_run:", workflow)
        self.assertIn("python build_index.py --check", workflow)
        self.assertIn("inputs.dry_run != true", workflow)


if __name__ == "__main__":
    unittest.main()
