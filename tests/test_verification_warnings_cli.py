"""Real advisory CLI against existing completion CLI fixture receipts."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "shared/scripts/verification_warnings.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fixture = load("completion_fixture", ROOT / "shared/scripts/tests/test_doc_evidence.py")
backend = load("warnings_backend", BACKEND)


class AdvisoryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.CompletionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.state = self.fixture.base / "state"
        self.environment = dict(os.environ, MRCALL_VERIFICATION_WARNINGS_STATE=str(self.state))
        self.old_state = os.environ.get("MRCALL_VERIFICATION_WARNINGS_STATE")
        os.environ["MRCALL_VERIFICATION_WARNINGS_STATE"] = str(self.state)
        self.addCleanup(self.restore_environment)

    def restore_environment(self):
        if self.old_state is None:
            os.environ.pop("MRCALL_VERIFICATION_WARNINGS_STATE", None)
        else:
            os.environ["MRCALL_VERIFICATION_WARNINGS_STATE"] = self.old_state

    def cli(self, *args, expected=0):
        argv = [sys.executable, str(BACKEND), *args]
        result = subprocess.run(argv, capture_output=True, text=True, env=self.environment)
        log = os.environ.get("MRCALL_WARNINGS_TEST_LOG")
        if log:
            with open(log, "a") as handle:
                handle.write(json.dumps({"test": self.id(), "argv": argv, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}) + "\n")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def inspect(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        value = self.cli("check", "--repo", str(self.root), "--task", self.fixture.task, "--json")
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertFalse(self.state.exists())
        return value["diagnostics"]

    def bind(self, session="fixture-session"):
        return self.cli("bind", "--runtime", "claude", "--session", session, "--repo", str(self.root), "--task", self.fixture.task)

    def test_missing_current_failed_changed_and_stale_actual_receipts(self):
        f = self.fixture
        f.initialize("fastpath")
        f.lead_closure(False)
        missing = self.inspect()[0]
        self.assertEqual(missing["reasons"], ["missing receipt"])
        self.assertIn(str(fixture.CHECKER.resolve()), missing["action"])
        self.assertIn("--input PATH_TO_ARGV_JSON", missing["action"])
        self.assertIn("actual JSON file", missing["action"])
        self.assertIn("not a runnable command", missing["action"])
        f.call("check", expected=1)
        f.call("focused", {"argv": [sys.executable, "src/tool.py"]})
        self.assertEqual(self.inspect(), [])
        f.call("focused", {"argv": [sys.executable, "-c", "raise SystemExit(7)"]}, expected=1)
        self.assertIn("command failed", self.inspect()[0]["reasons"][0])
        f.call("focused", {"argv": [sys.executable, "-c", "from pathlib import Path; Path('src/tool.py').write_text('print(42)\\n')"]}, expected=1)
        self.assertIn("command changed content or content evidence missing", self.inspect()[0]["reasons"])
        f.call("focused", {"argv": [sys.executable, "src/tool.py"]})
        (self.root / "src/tool.py").write_text("print('changed')\n")
        self.assertEqual(self.inspect()[0]["reasons"], ["stale content snapshot"])

    def test_mechanical_receipt_and_finalized_history_are_quiet(self):
        f = self.fixture
        f.initialize()
        self.assertEqual(self.inspect()[0]["obligation"], "mechanical")
        f.close(initialize=False)
        self.assertEqual(self.inspect(), [])
        f.call("finalize")
        f.git("add", ".")
        f.git("commit", "-m", "later commit")
        Path(f.workflows["doc_end"]).unlink()
        self.assertEqual(self.inspect(), [])

    def test_explicit_binding_dedupe_recurrence_cleanup_and_worktree(self):
        f = self.fixture
        f.initialize("fastpath")
        f.lead_closure(False)
        self.assertIsNone(backend.evaluate("claude", None, str(self.root)))
        self.assertIsNone(backend.evaluate("claude", "unbound", str(self.root)))
        self.bind()
        self.assertTrue(backend.evaluate("claude", "fixture-session", str(self.root)))
        self.assertIsNone(backend.evaluate("claude", "fixture-session", str(self.root)))
        f.call("focused", {"argv": [sys.executable, "src/tool.py"]})
        self.assertIsNone(backend.evaluate("claude", "fixture-session", str(self.root)))
        (self.root / "src/tool.py").write_text("print(43)\n")
        self.assertTrue(backend.evaluate("claude", "fixture-session", str(self.root / "src")))
        self.assertIsNone(backend.evaluate("codex", "fixture-session", str(self.root)))
        other = f.base / "worktree"
        f.git("worktree", "add", "-b", "other", str(other))
        self.assertIsNone(backend.evaluate("claude", "fixture-session", str(other)))
        f.call("focused", {"argv": [sys.executable, "src/tool.py"]})
        self.assertIsNone(backend.evaluate("claude", "fixture-session", str(self.root)))
        f.record().write_text("broken JSON")
        self.assertTrue(backend.evaluate("claude", "fixture-session", str(self.root)))
        values = self.cli("status")["bindings"]
        self.assertEqual(len(values), 1)
        for path in self.state.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.state.stat().st_mode), 0o700)
        self.cli("unbind", "--runtime", "claude", "--session", "fixture-session")
        self.assertEqual(self.cli("status")["bindings"], [])
        self.assertIsNone(backend.evaluate("claude", "fixture-session", str(self.root)))

    def test_bad_task_binding_and_malformed_record_are_zero_exit_diagnostics(self):
        self.fixture.initialize("fastpath")
        self.cli("bind", "--runtime", "claude", "--session", "../escape", "--repo", str(self.root), "--task", self.fixture.task, expected=1)
        self.assertFalse(self.state.exists())
        self.cli("bind", "--runtime", "claude", "--session", "valid", "--repo", str(self.root), "--task", "unrelated-task", expected=1)
        self.assertFalse(self.state.exists())
        self.fixture.record().write_text("[]")
        self.assertEqual(self.inspect()[0]["obligation"], "evidence")
        result = self.cli("check", "--repo", str(self.root), "--task", "../escape", "--json")
        self.assertTrue(result["diagnostics"])

    def test_checker_unavailable_is_nonblocking_bound_diagnostic(self):
        self.fixture.initialize("fastpath")
        self.bind()
        original = backend.modules
        backend.modules = lambda: (_ for _ in ()).throw(OSError("checker unavailable"))
        try:
            self.assertIn("checker unavailable", backend.evaluate("claude", "fixture-session", str(self.root)))
        finally:
            backend.modules = original


if __name__ == "__main__":
    unittest.main()
