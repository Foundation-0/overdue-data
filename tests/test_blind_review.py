import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/"pilot/blind_review_summary.py"
s=importlib.util.spec_from_file_location("review",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReviewTests(unittest.TestCase):
    def test_disagreement(self):
        r=m.summarize({"a":"typo","b":"real case"},{"a":"typo","b":"unclear"})
        self.assertEqual(r["agreements"],1)
        self.assertAlmostEqual(r["cohen_kappa"],1/3)
        self.assertNotIn("a",r)
    def test_same_class(self):
        self.assertIsNone(m.summarize({"a":"typo"},{"a":"typo"})["cohen_kappa"])
    def test_mismatched_samples(self):
        with self.assertRaises(ValueError):m.summarize({"a":"typo"},{"b":"typo"})
if __name__=="__main__":unittest.main()
