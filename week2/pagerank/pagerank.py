import os
import random
import re
import sys

DAMPING = 0.85         # This represents the damping factor
SAMPLES = 10000        # Number of samples to estimate PageRank using sampling method
PRECISION = 100000       # From 0 to PRECISION is where number is taken


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    The return value of the function should be a Python dictionary
    with one key for each page in the corpus. Each key should be
    mapped to a value representing the probability that a random
    surfer would choose that page next. The values in this returned
    probability distribution should sum to 1.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = {new_key: 0 for new_key in list(corpus.keys())}

    if len(corpus[page]) == 0:
        for link in probability_distribution:
            probability_distribution[link] = 1/len(corpus)
    else:
        corpus_probability = (1-damping_factor) / len(corpus)   # Probability of choosing page from corpus

        page_links = corpus[page]
        num_links = len(page_links)
        links_probability = damping_factor / num_links          # Probability of choosing link from page

        for link in page_links:
            probability_distribution[link] += links_probability

        for link in probability_distribution:
            probability_distribution[link] += corpus_probability
            probability_distribution[link] = round(probability_distribution[link], 5)

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    visit_count = {new_key: 0 for new_key in list(corpus.keys())}

    # 1. Choose first page randomly
    page_list = list(corpus.keys())
    sample = page_list[random.randint(0, len(corpus)-1)]

    # 2. Populate visit dictionary
    for x in range(n):
        # a. Generate rand num b/w 0 and 1 to determine sampling technique
        rand_num = random.randint(0, PRECISION)/PRECISION

        # b. Determine sample method, get sample
        if rand_num > damping_factor:
            sample = page_list[random.randint(0, len(corpus)-1)]
        else:
            # c. Generate transition model, calculate cutoffs, generate new random sample int
            cutoffs = calculate_cutoffs(transition_model(corpus, sample, damping_factor))
            rand_num = random.randint(0, PRECISION) / PRECISION

            for page in cutoffs:
                if cutoffs[page] >= rand_num:
                    sample = page
                    break

        visit_count[sample] += 1

    # 3. Calculate Ratios
    visit_ratio = {page: value / n for page, value in visit_count.items()}
    return visit_ratio


def calculate_cutoffs(trans_model):
    """
    Given a transition model (dictionary), translates the dictionary to cutoff form
    Each key will hold the upper limit of their range of "landed" value
    """
    trans_sum = 0
    cutoffs = {}

    for page in trans_model:
        trans_sum += trans_model[page]
        cutoffs[page] = trans_sum

    return cutoffs

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # 1. Initialize PageRank dictionary to 1/N
    page_ranks = {key: 1/len(corpus) for key in list(corpus.keys())}

    # 2. Iterate until difference < .001 for all updates
    repeat = True
    while repeat:
        repeat = False
        for page in corpus:
            new_value = calculate_pagerank(page, corpus, page_ranks, damping_factor)
            if abs(new_value - page_ranks[page]) > .001:
                repeat = True
            page_ranks[page] = new_value
    return page_ranks


def calculate_pagerank(p, corpus, page_ranks, d):
    """
    Calculates an individual page rank based on existing page ranks
    and returns the value.
    """
    first_term = (1 - d)/len(page_ranks)

    # Figure out what pages link to page p
    links = [page for page in corpus if p in corpus[page]]

    # Calculate summation part of second term
    summation = 0
    for i in links:
        summation += (page_ranks[i]/len(corpus[i]))

    return first_term + summation * d


if __name__ == "__main__":
    main()
