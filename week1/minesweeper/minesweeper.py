import itertools
import random
import copy


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.safes = set()  # Known safe cells #TODO: Determine if I even want to use these
        self.mines = set()  # Known mine cells

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        else:
            self.cells.remove(cell)
            self.count -= 1
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        else:
            self.cells.remove(cell)
        return


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) Mark cell as a move that has been made
        self.moves_made.add(cell)
        # 2) Mark the cell as safe
        self.mark_safe(cell)
        # 3) Add a new sentence to the AI's knowledge based on the value of 'cell' and 'count'
        cells = self.surrounding_cells(cell)
        sentence = Sentence(cells, count)
        self.knowledge.append(sentence)
        # 4) Mark any additional cells as safe or as mines if it can be concluded based on AI's knowledge
        self.mark_cells()

        # 5) Add any new sentences to AI's knowledge if they can be inferred from existing knowledge
        inferences = self.inferences()
        while inferences:
            for sentence in inferences:
                self.knowledge.append(sentence)

            # mark additional cells as safe or mines
            self.mark_cells()
            inferences = self.inferences()

    def inferences(self):
        new_sentences = []
        remove_sentences = []

        for sentence1 in self.knowledge:  # For each sentence, check if it is a subset of any sentences in knowledge
            if sentence1.cells == set():
                remove_sentences.append(sentence1)
                continue
            for sentence2 in self.knowledge:
                if sentence2.cells == set():
                    remove_sentences.append(sentence2)
                if sentence1 == sentence2:
                    continue
                if sentence1.cells.issubset(sentence2.cells):  # If set1 is a subset of set2
                    new_cells = sentence2.cells.difference(sentence1.cells)
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)
        self.knowledge = [x for x in self.knowledge if x not in remove_sentences]
        return new_sentences

    def mark_cells(self):
        repeat = True
        while repeat:
            repeat = False
            for sentence in self.knowledge:
                known_safes_copy = copy.deepcopy(sentence.known_safes())
                for cell in known_safes_copy:
                    self.mark_safe(cell)
                    repeat = True
                known_mines_copy = copy.deepcopy(sentence.known_mines())
                for cell in known_mines_copy:
                    print("FOUND MINE")
                    self.mark_mine(cell)
                    repeat = True
        self.knowledge = [x for x in self.knowledge if len(x.cells) != 0]

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0:
            return None
        for x in self.safes:
            if x not in self.moves_made:
                return x
        return None  # No safe cell not already played has been found

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for cell in range(self.height * self.width):  # TODO: This is kinda arbitrary loop
            random_i = random.randint(0, self.height - 1)
            random_j = random.randint(0, self.width - 1)
            cell = (random_i, random_j)
            if cell not in self.mines and cell not in self.moves_made:
                return cell
        return None

    def surrounding_cells(self, cell):
        """
        Returns a set of surrounding cells that are within board limits
        and the status is unknown (i.e. not in moves_made, safes or mines)
        """
        i, j = cell
        neighbors = set()
        for a in range(max(0, i-1), min(i+2, self.height)):
            for b in range(max(0, j-1), min(j+2, self.width)):
                if (a, b) != (i, j):
                    neighbors.add((a, b))
        return neighbors
