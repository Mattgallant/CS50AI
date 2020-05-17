import unittest
from week2.heredity.heredity import joint_probability

class TestHeredity(unittest.TestCase):
    def test_jp0(self):
        people = {
            'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James', 'trait': None},
            'James': {'name': 'James', 'mother': None, 'father': None, 'trait': True},
            'Lily': {'name': 'Lily', 'mother': None, 'father': None, 'trait': False}
        }
        one_gene = {"Harry"}
        two_genes = {"James"}
        has_trait = {"James"}
        self.assertEqual(.0026643247488, joint_probability(people, one_gene, two_genes, has_trait))


if __name__ == '__main__':
    unittest.main()
