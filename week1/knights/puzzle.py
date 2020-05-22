# from week1.knights.logic import *
from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

""" Implication(AKnight, sentenceA),
    Implication(AKnave, Not(sentenceA)),
    Implication(BKnight, sentenceB),
    Implication(BKnave, Not(sentenceB)),
"""

# Structure knowledge about player A
structureA_knowledge = And(
    Or(AKnight, AKnave),                # Must be one
    Implication(AKnight, Not(AKnave)),  # If Knight cannot be Knave
    Implication(AKnave, Not(AKnight)),  # If Knave cannot be Knight
)

structureB_knowledge = And(
    Or(BKnight, BKnave),                # Must be one
    Implication(BKnight, Not(BKnave)),  # If Knight cannot be Knave
    Implication(BKnave, Not(BKnight)),  # If Knave cannot be Knight
)

structureC_knowledge = And(
    Or(CKnight, CKnave),                # Must be one
    Implication(CKnight, Not(CKnave)),  # If Knight cannot be Knave
    Implication(CKnave, Not(CKnight)),  # If Knave cannot be Knight
)

# Puzzle 0
# A says "I am both a knight and a knave."
sentenceA = And(AKnight, AKnave)
knowledge0 = And(
    # Structure of problem
    structureA_knowledge,
    Implication(AKnight, sentenceA),
    Implication(AKnave, Not(sentenceA))
)

# Puzzle 1
# A says "We are both knaves."
sentenceA = And(AKnave, BKnave)
# B says nothing.
knowledge1 = And(
    structureA_knowledge,
    structureB_knowledge,
    Biconditional(AKnight, sentenceA),
)

# Puzzle 2
# A says "We are the same kind."
sentenceA = Or(And(AKnave, BKnave), And(AKnight, BKnight))
# B says "We are of different kinds."
sentenceB = Or(And(AKnave, BKnight), And(AKnight, BKnave))
knowledge2 = And(
    structureA_knowledge,
    structureB_knowledge,

    Biconditional(AKnight, sentenceA),
    Biconditional(BKnight, sentenceB)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
sentenceA = Or(AKnave, AKnight)
# B says "A said 'I am a knave'."
sentenceB1 = AKnave
# B says "C is a knave."
sentenceB2 = CKnave
# C says "A is a knight."
sentenceC = AKnight
knowledge3 = And(
    structureA_knowledge,
    structureB_knowledge,
    structureC_knowledge,

    Biconditional(AKnight, sentenceA),
    Biconditional(BKnight, sentenceB1),
    Biconditional(BKnight, sentenceB2),
    Biconditional(CKnight, sentenceC),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
