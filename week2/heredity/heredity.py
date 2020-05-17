import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    # Conditional probability that a person exhibits a trait
    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability of all of the listed events taking place.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    final_product = 1  # Holds the product of each event's probability

    for person in people:
        # 1. Get father, mother, values of father, mother and person genes
        father = people[person]["father"]
        mother = people[person]["mother"]

        if father is not None:
            # Determine parent gene counts
            father_genes, mother_genes = get_parent_genes(one_gene, two_genes, father, mother)
        person_genes = get_person_genes(one_gene, two_genes, person)

        # 2. Calculate probability of 0, 1, 2 gene
        if person in one_gene:
            if father is None:
                gene_probability = PROBS["gene"][1]
            else:
                if father_genes == 0:
                    father_factor1 = PROBS["mutation"]
                    father_factor2 = 1- PROBS["mutation"]
                elif father_genes == 1:
                    father_factor1 = .5
                    father_factor2 = .5
                elif father_genes == 2:
                    father_factor1 = 1- PROBS["mutation"]
                    father_factor2 = PROBS["mutation"]

                if mother_genes == 0:
                    mother_factor2= PROBS["mutation"]
                    mother_factor1 = 1- PROBS["mutation"]
                elif mother_genes == 1:
                    mother_factor2 = .5
                    mother_factor1 = .5
                elif mother_genes == 2:
                    mother_factor2 = 1- PROBS["mutation"]
                    mother_factor1 = PROBS["mutation"]

                gene_probability = father_factor1 * mother_factor1 + father_factor2 * mother_factor2

        elif person in two_genes:
            if father is None:
                gene_probability = PROBS["gene"][2]
            else:
                if father_genes == 0:
                    father_factor = PROBS["mutation"]
                elif father_genes == 1:
                    father_factor = .5
                elif father_genes == 2:
                    father_factor = 1- PROBS["mutation"]

                if mother_genes == 0:
                    mother_factor = PROBS["mutation"]
                elif mother_genes == 1:
                    mother_factor = .5
                elif mother_genes == 2:
                    mother_factor = 1- PROBS["mutation"]

                gene_probability = mother_factor * father_factor
        else:
            # Probability of 0 genes for this person
            if father is None:
                gene_probability = PROBS["gene"][0]
            else:
                if father_genes == 0:
                    father_factor = 1 - PROBS["mutation"]
                elif father_genes == 1:
                    father_factor = .5
                elif father_genes == 2:
                    father_factor = PROBS["mutation"]

                if mother_genes == 0:
                    mother_factor = 1 - PROBS["mutation"]
                elif mother_genes == 1:
                    mother_factor = .5
                elif mother_genes == 2:
                    mother_factor = PROBS["mutation"]

                gene_probability = mother_factor * father_factor

        # 3. Calculate probability of trait
        trait_probability = PROBS["trait"][person_genes][person in have_trait]

        # 4. Multiply together, add to final product
        person_product = trait_probability * gene_probability
        final_product *= person_product

    return final_product


def get_parent_genes(one_gene, two_genes, father, mother):
    """
    Determines how many genes both the father and mother have.
    Returns as a (father_genes, mother_genes) tuple
    """

    father_genes = get_person_genes(one_gene, two_genes, father)
    mother_genes = get_person_genes(one_gene, two_genes, mother)
    return father_genes, mother_genes


def get_person_genes(one_gene, two_genes, person):
    """
    Determines how many genes person has. Returns values.
    """
    if person in one_gene:
        person_genes = 1
    elif person in two_genes:
        person_genes = 2
    else:
        person_genes = 0

    return person_genes


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # 1. Get data about person
        if person in two_genes:
            gene = 2
        elif person in one_gene:
            gene = 1
        else:
            gene = 0

        # 2. Update gene distribution
        probabilities[person]["gene"][gene] += p

        # 3. Update trait distribution
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # 1. Normalize gene distribution
        gene_sum = sum(probabilities[person]["gene"].values())
        normalizing_factor = 1/gene_sum
        for key, value in probabilities[person]["gene"].items():
            probabilities[person]["gene"][key] = value*normalizing_factor

        # 2. Normalize trait distribution
        trait_sum = sum(probabilities[person]["trait"].values())
        normalizing_factor = 1/trait_sum
        for key, value in probabilities[person]["trait"].items():
            probabilities[person]["trait"][key] = value*normalizing_factor

if __name__ == "__main__":
    main()
