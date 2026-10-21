"""Offline regression checks; no app imports, credentials, or API calls."""
import ast
import contextlib
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]


class SecretOutputTests(unittest.TestCase):
    def select_model(self, key, model="GPT-3.5"):
        source = ast.parse((ROOT / "api_4.py").read_text(encoding="utf-8"))
        function = next(node for node in source.body
                        if isinstance(node, ast.FunctionDef) and node.name == "select_model")
        st = Mock()
        st.sidebar.radio.return_value = model
        st.sidebar.slider.return_value = 0.7
        client = Mock()
        # Substitute getenv before executing any app code; never read the real environment.
        getenv = Mock(return_value=key)
        scope = {"os": SimpleNamespace(getenv=getenv), "st": st, "ChatOpenAI": client}
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(ast.Module(body=[function], type_ignores=[]), "api_4.py", "exec"), scope)
            result = scope["select_model"]()
        getenv.assert_called_once_with("OPENAI_API_KEY")
        return result, st, client, output.getvalue()

    def test_key_reaches_client_but_not_ui_or_console(self):
        sentinel = "dummy-api-key-output-regression-sentinel"
        for label, name in [("GPT-3.5", "gpt-3.5-turbo"), ("GPT-4", "gpt-4")]:
            with self.subTest(model=label):
                result, st, client, output = self.select_model(sentinel, label)
                client.assert_called_once_with(temperature=0.7, model_name=name,
                                               openai_api_key=sentinel)
                self.assertIs(result, client.return_value)
                self.assertNotIn(sentinel, repr(st.mock_calls))
                self.assertNotIn(sentinel, output)
                st.error.assert_not_called()

    def test_missing_key_still_stops_with_safe_error(self):
        for key in (None, ""):
            with self.subTest(key=key):
                result, st, client, _ = self.select_model(key)
                self.assertIsNone(result)
                client.assert_not_called()
                st.error.assert_called_once_with("OPENAI_API_KEY is not set.")

    def test_workflow_passes_key_only_as_environment_variable(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        references = [line.strip() for line in workflow.splitlines()
                      if "OPENAI_API_KEY" in line]
        self.assertEqual(references, ["OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}"])
        self.assertIn("run: streamlit run api_4.py", workflow)


if __name__ == "__main__":
    unittest.main()
