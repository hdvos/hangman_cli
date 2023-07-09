import random 
from hangman_images.hangman_figures import hangman_figures
import os
from collections import Counter


class HangmanSolver(object):
    def __init__(self):
        pass



class HangmanGame(object):
    def __init__(self, player_role = "guess", wordlist_file = "./wordlists/NL.txt"):
        self.player_role = player_role
        self.wordlist_file = wordlist_file
        self.wordlist = self._load_wordlist()
        self.hangman_figures = hangman_figures
        self.max_mistakes = len(hangman_figures) -1

        self.wordcounterdict = dict()



    def _load_wordlist(self):
        with open(self.wordlist_file, "rt") as f:
            content = f.read()

        wordlist = content.split("\\")
        
        print(f"Loaded wordlist from {self.wordlist_file}. \nWordlist contains {len(wordlist)} words.")

        return wordlist

    def _print_game_state(self, n_mistakes, good_guesses, all_guesses):
        rows, columns = os.popen('stty size', 'r').read().split()
        os.system('cls' if os.name == 'nt' else 'clear')
        print("-"*int(columns))
        print(f"{n_mistakes} mistakes of {self.max_mistakes}")
        print(hangman_figures[n_mistakes])
        print()
        print("".join(good_guesses))
        print("".join([str(i) for i in list(range(1, len(good_guesses) + 1))]))
        print()
        print("".join(all_guesses))

        print("-"*int(columns))


    def _play_game_as_host(self):
        print("\n")
        print("*"*30)
        print("Lets start a game!")
        print("I will pick a word.")
        
        word = random.choice(self.wordlist)
        
        print(f"I picked a word with {len(word)} letters.")
        input("press enter to continue")

        game_solved = False
        game_failed = False
        mistakes = 0
        good_guesses = ['.' for _ in range(len(word))]
        all_guesses = ["_"]*26
        while (not game_solved) and (not game_failed):
            self._print_game_state(mistakes, good_guesses, all_guesses)
            letter = input("Guess a letter and press enter: ") # todo; check wether a single letter is entered
            letter = letter.lower()

            if letter in word:
                indices = [pos for pos, char in enumerate(word) if char == letter]
                for index in indices:
                    good_guesses[index] = letter
                all_guesses[ord(letter) - 97] = letter
            else:
                mistakes += 1
                all_guesses[ord(letter) - 97] = letter
        
            if "".join(good_guesses) == word:
                game_solved = True
            elif mistakes >= self.max_mistakes :
                game_failed = True
        
        if game_solved:
            self._print_game_state(mistakes,good_guesses,all_guesses)
            print(f"Congratulations!!! You won! The word was indeed '{word}'!")
        elif game_failed:
            self._print_game_state(mistakes,good_guesses,all_guesses)
            print(f"Too bad. You hang. The word I had in mind was '{word}'")
        
    def _ask_nr_letters(self):
        nr_letters = input("How many letters does your word have? ")

        return int(nr_letters)


    def _count_letters(self, words_left):
        lettercount = Counter()
        for word in words_left:

            if not word in self.wordcounterdict.keys():
                self.wordcounterdict[word] = Counter(word)
                
            lettercount += self.wordcounterdict[word]
        return lettercount
                
    def _guess_most_occurring(self,words_left , past_guesses):
        lettercount = self._count_letters(words_left)
        for letter,count in sorted(list(lettercount.items()), key=lambda x:x[1])[::-1]:
            if not letter in past_guesses:
                return letter

        raise RuntimeError("all letters are guessed and no result has come up.")




    def _make_guess(self, words_left, past_guesses, strategy = "most_occurring"):
        if strategy == "most_occurring":
            return self._guess_most_occurring(words_left, past_guesses)
        else:
            raise NotImplementedError(f"No strategy known named: '{strategy}'")

    def _filter_words(self, words_left, good_guesses):
        filtered = []

        for word in words_left:
            match = True
            for char1, char2 in zip(list(word), good_guesses):
                if char2 == ".":
                    pass
                elif char1 != char2:
                    match = False
            if match:
                filtered.append(word)
        
        return filtered



    def _play_game_as_guesser(self):
        nr_letters = self._ask_nr_letters()
        
        print(f"nr words left: {len(self.wordlist)}")
        words_left = [word for word in self.wordlist if len(word) == nr_letters]
        print(f"nr words left: {len(words_left)}")

        game_solved = False
        game_failed = False
        mistakes = 0
        good_guesses = ['.' for _ in range(nr_letters)]
        all_guesses = ["_"]*26
        while (not game_solved) and (not game_failed):
            self._print_game_state(mistakes, good_guesses, all_guesses)
            print(f"\nnr words left: {len(words_left)}\n")
            guess_letter = self._make_guess(words_left, all_guesses)

            all_guesses[ord(guess_letter) - 97] = guess_letter

            print(f"I guess the letter {guess_letter}")
            response = input("Is this correct? y/n ").lower()
            if response == "y":
                indices = input("Enter the indices (starting at 1) of the letters separated by spaces. Press enter when ready ")
                indices = indices.strip().split(' ')
                indices = [int(index.strip()) for index in indices]

                for index in indices:
                    good_guesses[index-1] = guess_letter
                
                words_left = self._filter_words(words_left, good_guesses)
            
            elif response == 'n':
                mistakes += 1
                words_left = [x for x in words_left if not guess_letter in x]
            else:
                raise ValueError("invalid response")

            

            if not '.' in good_guesses:
                game_solved = True
            elif mistakes >= self.max_mistakes :
                game_failed = True    
        

        if game_solved:
            self._print_game_state(mistakes,good_guesses,all_guesses)
            print(f"I think I found it!")
            response = input(f"Is your word '{''.join(good_guesses)}'? (y/n) ")
            if response == 'y':
                print("yay I won!")
            else:
                print("Then the word you chose is not in my dictionary")
        elif game_failed:
            self._print_game_state(mistakes,good_guesses,all_guesses)
            print(f"I lost. Congratulations")




    def play_game(self):
        if self.player_role == "guess":
            self._play_game_as_host()
        elif self.player_role == "host":
            self._play_game_as_guesser()
        else:
            raise(NotImplementedError(f"Did not implement the '{self.player_role}'-player role yet."))

if __name__ == "__main__":
    game = HangmanGame(player_role="host")
    game.play_game()