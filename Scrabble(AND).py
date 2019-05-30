from itertools import permutations
letters = input("Jakie literki tam sie zawieraja? ")
count_word = int(input("Iloliterowe jest to slowo? "))
words = {''.join(x) for x in permutations(letters,count_word)}

with open('/storage/emulated/0/Download/slowa.txt') as f: # https://sjp.pl/slownik/growy/sjp-20190528.zip
	for linia in f:
		if linia.strip() in words:
			if len(linia.strip()) == count_word:
				print (linia.strip())
