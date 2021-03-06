import sys
import collections

from week3.crossword.crossword import *
# from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains.keys():
            remove_set = set()
            # Find words that need to be removed
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    remove_set.add(word)
            # Remove words
            for word in remove_set:
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x, y] is None:
            return False
        else:
            xspot, yspot = self.crossword.overlaps[x, y]  # The positions where the two variables overlap

        # Find words in x domain that need to be removed
        remove_set = set()
        for xword in self.domains[x]:
            remove = True  # Remove by default unless match
            for yword in self.domains[y]:
                if xword[xspot] == yword[yspot]:  # Found a match
                    remove = False
                    break
            if remove:
                remove_set.add(xword)

        # Remove words that are not arc consistent with variable y from x domain
        for word in remove_set:
            self.domains[x].remove(word)

        if remove_set != set():
            return True
        else:
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = self.find_arcs()
        else:
            queue = arcs
        queue = collections.deque(queue)  # Allows for faster pops and pop from left side (not stack behavior)

        # AC-3 algo from week 3 slides
        while len(queue) != 0:
            (x, y) = queue.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False  # A domain ended up empty, return false
                for z in (self.crossword.neighbors(x) - {y}):
                    queue.append((z, x))
        return True

    def find_arcs(self):
        """
        Finds and returns a list of all arcs (edges).
        """
        arcs = list()
        for v1 in self.crossword.variables:
            for v2 in self.crossword.neighbors(v1):
                if (v2,
                    v1) not in arcs:  # TODO: perhaps don't want this here? Not sure if (v1, v2) == (v2, v1) in our representation
                    arcs.append((v1, v2))
        return arcs

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment or assignment[variable] is None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Condition 1: All values are distinct
        values = set()
        for value in assignment.values():
            if value in values:
                return False
            values.add(value)

        # Condition 2: Every value has a correct length
        for variable, value in assignment.items():
            if variable.length != len(value):
                return False

        # Condition 3: No conflicts b/w neighboring values
        for var_x in assignment:
            for var_y in assignment:
                if var_x is var_y: continue
                overlap = self.crossword.overlaps[var_x, var_y]
                if overlap is not None:
                    (x_spot, y_spot) = overlap
                    if assignment[var_x][x_spot] != assignment[var_y][y_spot]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ruleout_values = {}
        for value in self.domains[var]:
            n = 0
            for neighbor in self.crossword.neighbors(var):
                for neighbor_value in self.domains[neighbor]:
                    # For every neighbor of var, check every word in their domain and count conflicts
                    var_spot, neighbor_spot = self.crossword.overlaps[var, neighbor]
                    if value[var_spot] != neighbor_value[neighbor_spot]:
                        n += 1
                ruleout_values[value] = n

        ruleout_values = {k: v for k, v in sorted(ruleout_values.items(), key=lambda x: x[1])}
        return ruleout_values.keys()

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = set(self.crossword.variables) - set(assignment.keys())

        # Get set of variables with fewest remaining values in domain
        min_length = len(self.crossword.words)  # Start with this b/c it is max any domain can be
        min_set = set()
        for variable in unassigned:
            var_length = len(self.domains[variable])
            if var_length == min_length:
                min_set.add(variable)
            elif var_length < min_length:
                min_set.clear()
                min_length = var_length
                min_set.add(variable)

        # Return variable with smallest domain OR w/ smallest domain and largest degree
        if len(min_set) == 1:
            return min_set.pop()
        else:
            most_neighbors = min_set.pop()
            number_neighbors = len(self.crossword.neighbors(most_neighbors))
            for variable in min_set:
                neighbors = len(self.crossword.neighbors(variable))
                if neighbors > number_neighbors:
                    most_neighbors = variable
                    number_neighbors = neighbors
            return most_neighbors

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.

        Algorithm taken from CS50 week 3 slides.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable, assignment):  # Consider all values in var's domain
            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[variable]  # This value didn't work, remove and retry.
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
