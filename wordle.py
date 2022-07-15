import string
from random import randint
from typing import List


def read_answer_file(file_path: str, word_count=None) -> list:
    with open(file_path, "r") as f:
        words = [w.replace("\n", "").lower() for w in f.readlines()]

    if word_count:
        return words[:word_count]
    else:
        return words


def get_five_letter_words(
    filename=None,
    skip_plural=False,
    skip_past=False,
    skip_multiples=False,
    skip_letters="",
) -> List:
    if not filename:
        filename = "/usr/share/dict/words"

    # Add all 5-letter words to list
    fives_list = []
    with open(filename, "r") as wordfile:
        for word in wordfile.read().splitlines():
            if len(word) == 5 and word.isalpha() and word.islower():
                if (
                    (skip_plural and word[-1] == "s")
                    or (skip_past and word.find("ed") == 3)
                    or (skip_multiples and len({s for s in word}) != len(word))
                    or len(set(skip_letters).intersection(word)) > 0
                ):
                    continue
                else:
                    fives_list.append(word)

    return fives_list


def get_letter_frequency(word_list: List[str]) -> dict:
    # Find the frequency of each letter in each position
    letters = {pos: {} for pos in range(5)}
    for word in word_list:
        for pos in range(5):
            letter_count = letters[pos].get(word[pos])
            if letter_count:
                letters[pos][word[pos]] = letter_count + 1
            else:
                # letters[pos] = 0, 1, 2, 3, 4
                # word[pos] = a, b, c, etc.
                letters[pos][word[pos]] = 1

    return letters


def get_word_frequency_by_letter(word_list: List[str]):
    # For each 5-letter word in a list, calculate total based on frequency of that letter in all words
    letter_values = {n: 0 for n in list(string.ascii_lowercase)}
    removed = []
    for word in word_list:
        for letter in word:
            letter_val = letter_values.get(letter)
            if letter_val is not None:
                letter_values[letter] += 1
            else:
                if word not in removed:
                    removed.append(word)
                    # print(word)

    for word in removed:
        word_list.remove(word)

    return letter_values


def score_by_letter_position(word_list: List[str], letter_values: dict):
    # For each 5-letter word, calculate total based on frequency of that letter in that position
    word_values = {word: 0 for word in word_list}
    for word in word_list:
        total = 0
        for pos, letter in enumerate(word):
            value = letter_values[pos][letter]
            total += value
        word_values[word] = total

    return word_values


def score_by_letter_frequency(word_list: List[str], letter_values: dict):
    # For each 5-letter word, calculate total based on frequency of that letter in that position
    word_values = {word: 0 for word in word_list}
    for word in word_list:
        total = 0
        for letter in word:
            value = letter_values[letter]
            total += value
        word_values[word] = total

    return word_values


def find_next_word(skip_letters=None):
    if skip_letters is None:
        skip_letters = ""

    word_list = get_five_letter_words(
        skip_plural=True, skip_past=True, skip_multiples=True, skip_letters=skip_letters
    )

    if not word_list:
        return

    letter_values = get_word_frequency_by_letter(word_list)
    word_values = score_by_letter_frequency(word_list, letter_values)

    # letters = get_letter_frequency(word_list)
    # word_values = score_by_letter_position(word_list, letters)
    # Sort descending by highest word total
    highest_words = dict(
        sorted(word_values.items(), key=lambda item: item[1], reverse=True)
    )
    top_word = list(highest_words.keys())[0]
    print(top_word)
    return top_word


def score_words_by_common_letters(word_list):
    letter_values = get_word_frequency_by_letter(word_list)
    word_values = score_by_letter_frequency(word_list, letter_values)

    # Sort descending by highest word total
    highest_words = dict(
        sorted(word_values.items(), key=lambda item: item[1], reverse=True)
    )

    return highest_words


def score_words_by_letter_positions(word_list):
    letters = get_letter_frequency(word_list)
    word_values = score_by_letter_position(word_list, letters)
    # Sort descending by highest word total
    highest_words = dict(
        sorted(word_values.items(), key=lambda item: item[1], reverse=True)
    )

    return highest_words


def check_word(word_list: list, target_word: str):
    valid_words = []
    for word in word_list:
        for i, letter in enumerate(word):
            if letter != target_word[i]:
                break
        else:
            valid_words.append(word)  # only executed if the inner loop did NOT break
        break  # only executed if the inner loop DID break


def play_wordle_game(target_word: str, first_guess="cares") -> str:
    word_list = get_five_letter_words(
        skip_plural=True, skip_past=True, skip_multiples=False
    )

    start_letter_list = [""] * 5
    # Create dict of lists for incorrectly guessed letter positions, don't re-use
    incorrect_pos = {i: [] for i in range(1, 6)}
    valid_letters = set()
    invalid_letters = set()

    def make_guess(guess: str, letter_list: list, guessed_words: list, n: int) -> list:
        if guess == target_word:
            print(f"Found target word {target_word} in {n} tries. Guessed {guessed_words}.")
            return guess, n

        # Check each letter of guess against target word, either match, valid, or invalid
        for i, letter in enumerate(guess):
            if letter == target_word[i]:
                letter_list[i] = letter
            elif target_word.find(letter) > -1:
                valid_letters.add(letter)
                incorrect_pos[i + 1].append(letter)
            else:
                invalid_letters.add(letter)

        valid_words = []
        for word in word_list:
            # If letter is blank, continue, if letter does not match known position, break
            # https://stackoverflow.com/questions/653509/breaking-out-of-nested-loops
            for i, letter in enumerate(word):
                if letter in incorrect_pos[i + 1]:
                    break
                elif letter_list[i] == "":
                    continue
                elif letter != letter_list[i]:
                    break
            else:
                # Only executed if the inner loop did NOT break
                # Valid word must contain all valid letters
                match_letters = list(set(word).intersection(valid_letters))

                # Valid word can't contain invalid letters
                nonmatch_letters = list(set(word).intersection(invalid_letters))

                if (
                    len(match_letters) == len(valid_letters)
                    and len(nonmatch_letters) == 0
                    and word not in guessed_words
                ):

                    valid_words.append(word)

            # Move onto next word if the inner loop DID break
            continue

        if len(valid_words) == 0:
            # raise RuntimeError("Target word not in default word list")
            print(f"Target word {target_word} not in default word list")
            return target_word, 0
        elif n == 6:
            print(f"Failed to guess target word {target_word} in 6 tries. Guessed {guessed_words}")
            return "", 7
        else:
            # Randomly select next guess from list of valid words
            next_guess = valid_words[randint(0, len(valid_words) - 1)]
            guessed_words.append(next_guess)
            n += 1

            # Recursively call make_guess using updated args
            return make_guess(next_guess, letter_list, guessed_words, n)

    return make_guess(first_guess, start_letter_list, [first_guess], 1)


def find_best(count: int) -> list:
    word_list = get_five_letter_words(
        skip_plural=True, skip_past=True, skip_multiples=True
    )

    word_score = score_words_by_common_letters(word_list)
    score_by_position = score_words_by_letter_positions(word_list)
    combined_score = {w: word_score[w] * score_by_position[w] for w in word_list}
    highest_word_scores = dict(
        sorted(combined_score.items(), key=lambda item: item[1], reverse=True)
    )
    highest_words = list(highest_word_scores.keys())[: count - 1]

    return highest_words


def find_consecutive():
    # Find the best consecutive, non-overlapping words to account for the most common letters
    used_letters = ""
    for n in range(3):
        top_word = find_next_word(used_letters)
        if top_word:
            used_letters += top_word
        else:
            break


def test_word(word: str, target_words: list):
    average_tries = 0

    for target in target_words:
        word, tries = play_wordle_game(target, word)

        if tries == 0:
            target_words.remove(word)
        else:
            average_tries += tries

    average_tries = average_tries / len(target_words)

    return average_tries


def test_multi_run(word: str, target_words: list, runs=100):
    average_of_averages = 0
    for t in range(runs):
        average_tries = test_word(word, target_words)
        average_of_averages += average_tries

    average_of_averages = average_of_averages / runs
    print(f"Average tries: {average_of_averages}")


if __name__ == "__main__":
    # target_words = [
    #     "reign",
    #     "scaly",
    #     "repel",
    #     "sling",
    #     "maybe",
    #     "edify",
    #     "sadly",
    #     "mango",
    # ]

    # best_words = find_best(100)
    # for word in best_words:
    #     average = test_word(word)
    #     print(f"Average tries for word '{word}': {average}")

    word = "spare"
    # target_words = read_answer_file("./answers.csv")
    target_words = ["divan"]
    average = test_word(word, target_words)
    print(f"Average tries for word '{word}': {average}")

    # test_multi_run("chain", 100)
