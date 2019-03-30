import unidecode

def remove_accents(input_word):
	
	return unidecode.unidecode(input_word)

print(remove_accents('Pokémon'))