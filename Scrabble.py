from itertools import permutations
letters = input("Jakie literki tam sie zawieraja? ") # What letters are in there?(repeated also)
count_word = int(input("Iloliterowe jest to slowo? ")) # How much letters does this word contain?
words = {''.join(x) for x in permutations(letters,count_word)}

with open('slowa.txt') as f: # https://sjp.pl/slownik/growy/sjp-20190528.zip
	for line in f:
		if line.strip() in words:
			if len(line.strip()) == count_word:
				print (line.strip())
