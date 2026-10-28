import importlib.util
from pathlib import Path
import unittest
p = Path(__file__).resolve().parents[1] / "pilot/batch_fulltext.py"
spec = importlib.util.spec_from_file_location("batch", p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class BatchTests(unittest.TestCase):
    def test_status_is_not_inferred_from_http(self):
        self.assertEqual(m.dataset_status(200, '{"message":"ok"}'), ("unknown", "unknown"))
        self.assertEqual(m.dataset_status(404, '{}'), ("unknown", "unknown"))
    def test_private_marker(self):
        self.assertEqual(m.dataset_status(403, '{"error":"DatasetNotYetReleased","repository":"PRIDE"}'),
                         ("private", "PRIDE"))
    def test_identifier_boundaries(self):
        token = "PXD" + "123456"
        self.assertEqual(m.ACCESSION.findall(token + "7 X" + token), [])
        self.assertEqual(m.ACCESSION.findall("(" + token + ")"), [token])
    def test_cache_rejects_repository(self):
        with self.assertRaises(ValueError):
            m.Client(p.parent, "someone@example.org")
if __name__ == "__main__": unittest.main()
