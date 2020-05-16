import unittest
from week2.pagerank.pagerank import transition_model


class TestPagerank(unittest.TestCase):
    def test_tm0(self):
        """
        Tests an example scenario
        """
        damping_factor = .85
        page = "1.html"
        corpus = {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}

        ret_dict = transition_model(corpus, page, damping_factor)
        self.assertEqual({"1.html": 0.05, "2.html": 0.475, "3.html": 0.475}, ret_dict)

    def test_tm1(self):
        """
        Tests if transition model's probabilities add up to 1
        """
        damping_factor = .85
        page = "1.html"
        corpus = {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}

        ret_dict = transition_model(corpus, page, damping_factor)
        self.assertEqual(1, sum(ret_dict.values()))

    def test_tm2(self):
        """
        Tests if transition model's probabilities add up to 1 in the case that page has no links
        """
        damping_factor = .85
        page = "1.html"
        corpus = {"1.html": {}, "2.html": {"3.html"}, "3.html": {"2.html"}}

        ret_dict = transition_model(corpus, page, damping_factor)
        self.assertEqual(1, sum(ret_dict.values()))

if __name__ == '__main__':
    unittest.main()
