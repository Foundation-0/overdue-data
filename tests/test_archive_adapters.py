import importlib.util
import json
from pathlib import Path
import unittest
s = importlib.util.spec_from_file_location("adapters", Path(__file__).resolve().parents[1]/"pilot/archive_adapters.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)

class AdapterTests(unittest.TestCase):
    def test_extraction_boundaries_and_duplicates(self):
        tokens = ["MTBLS"+"12", "ST"+"123456", "PRJNA"+"123", "PRJEB"+"12", "PRJDB"+"4"]
        for token in tokens:
            self.assertEqual(sum(map(len, m.extract("("+token+") "+token).values())), 1)
            self.assertEqual(sum(map(len, m.extract("X"+token+" "+token+"X").values())), 0)
        self.assertFalse(m.extract("ST"+"1234567")["Metabolomics Workbench"])

    def test_http_failures_do_not_imply_private(self):
        for status in (401, 403, 404, 429, 500):
            self.assertEqual(m.classify("MetaboLights", "MTBLS"+"12", status, "{}"), "unknown")

    def test_public_identity_required(self):
        acc = "ST"+"123456"
        self.assertEqual(m.classify("Metabolomics Workbench", acc, 200, json.dumps({"study_id": acc})), "public_metadata")
        self.assertEqual(m.classify("Metabolomics Workbench", acc, 200, '{"message":"success"}'), "unknown")

    def test_bioproject_exact_identity(self):
        acc = "PRJEB"+"12"
        self.assertEqual(m.classify("BioProject", acc, 200, '<Package><ArchiveID accession="'+acc+'"/></Package>'), "public_metadata")
        self.assertEqual(m.classify("BioProject", acc, 200, '<error>not found</error>'), "unknown")

    def test_aggregate_omits_ids_and_rejects_duplicates(self):
        record = {"archive":"MetaboLights", "accession":"MTBLS"+"12", "status":404, "body":"{}"}
        self.assertEqual(m.aggregate([record]), [{"archive":"MetaboLights", "status":"unknown", "count":1}])
        with self.assertRaises(ValueError): m.aggregate([record, record])

if __name__ == "__main__": unittest.main()
