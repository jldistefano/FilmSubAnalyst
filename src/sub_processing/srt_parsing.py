import srt
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

def load_srt(path):
	"""
	Parses a srt file and returns a list of its subtitles in the form of
	subtitle objects, from the srt library.
	:param1 path: String representing path to a .srt file
	:returns: A list of Subtitle objects from the srt library
	"""
	with open(path, 'r', encoding= "latin-1") as myfile:
		all_file_str = myfile.read()

	for i in range(0, len(all_file_str), 1):
		if (all_file_str[i] == '1'):
			all_file_str = all_file_str[i:]
			break
	myfile.close()
	return list(srt.parse(all_file_str))

def load_word_list(path):
	"""
	Converts a word_list file, output from get_word_list(), into a list of 
	words and second of appearance. [[word_1, time_1], [word_1, time_1], ...]
	Word # i = word_list[i][0]
	Word # i time of appearance = word_list[i][0] seconds
	:param1 path: String, path to file containing word_list. Output of get_word_list()
	:returns: A list of lists of a word and it's time of appearance, as formatted above
	"""
	word_list = []
	with open(path, 'r') as file:
		line = file.readline()
		while line:
			line_cont = line.split("\t")
			if (len(line_cont) == 4):
				word_list.append([line_cont[1], float(line_cont[3])])
			line = file.readline()
	file.close()
	return word_list

def load_word_count(path):
	"""
	Converts a word_count file, output from get_word_count(), into a list of 
	word's and frequency. [[word_most_freq, frequency], ... , [word_least_freq, frequency]]
	nth most frequent word = word_count[n][0]
	nth frequent word number of appearances = word_count[n][1]
	:param1 path: String, path to file containing word_list. Output of get_word_list()
	:returns: A list of lists of a word and it's time of appearance, as formatted above
	"""
	word_count = []
	with open(path, 'r') as file:
		line = file.readline()
		while line:
			line_cont = line.split("\t")
			if (len(line_cont) == 4):
				word_count.append([line_cont[1], int(line_cont[3])])
			line = file.readline()
	file.close()
	return word_count

def get_word_list_old(subtitle_list, dirname="custom"):
	"""
	Takes a list of Subtitle objects from the srt library, creates a list of tuples of
	individual words and their timestamps
	:param1 subtitle_list: List of Subtitle objects from the srt library
	:param2 write_path: Path file to write to
	:returns: Writes a list of list of words and times in seconds to word_list.json
	"""
	path = sys.path[0] + "/../../sub_files/txt/" + dirname
	if not (os.path.isdir(path)):
		os.mkdir(path)
	# Go through each subtitle and pick out each word, add word to list
	file = open(path + "/word_list.txt", 'w')
	i = 1
	for sub in subtitle_list:
		# Creates list of words by splitting sentence of subtitle
		word_list = sub.content.split()
		# Creates iterable object from words_list
		words = iter(word_list)
		# For each word in the list of words, add valid words and timestamps to word list
		for word in words:
			# Handles character names, ie) "HAN: How you feeling, kid? --> How you feeling, kid?
			if (word[-1] == ':'):
				continue
			# Handles sound effects, usually contained in (), [], <>, {}
			if ((word[0] == '(') or (word[0] == '[') or (word[0] == '{') or (word[0] == '<')):
				while ((word[-1] != ')') and (word[-1] != ']') and (word[-1] != '}') and (word[-1] != '>')):
					if (word_list[-1] == word):
						break
					word = words.__next__()
				continue
			# Remove any invalid characters (not letter or ' )   
			for char in ' ?.!/;:",$%^@~`_=+;|*#$–º♪':
				word = (word.replace(char,'')).lower()
			# Handles hyphenated words
			hyphenated = word.split("-")
			if (len(hyphenated) == 1) and (word != " ") and (word != ""):
				# If the resulting string is not empty, it is added to the word list
				file.write(str(i) + ")\t" + word + "\t\t" + str((sub.end).total_seconds()) + '\n')
				i += 1
			else:
				for subword in hyphenated:
					if ((subword != " ") and (subword != "")):
						file.write(str(i) + ")\t" + subword + "\t\t" + str((sub.end).total_seconds()) + '\n')
						i += 1
	return (path + "/word_list.txt")

def get_word_list(subtitle_list, dirname="custom"):
	"""
	Takes a list of Subtitle objects from the srt library, creates a list of tuples of
	individual words and their timestamps
	:param1 subtitle_list: List of Subtitle objects from the srt library
	:param2 write_path: Path file to write to
	:returns: Writes a list of list of words and times in seconds to word_list.json
	"""
	path = sys.path[0] + "/../../sub_files/txt/" + dirname
	if not (os.path.isdir(path)):
		os.mkdir(path)
	# Go through each subtitle and pick out each word, add word to list
	file = open(path + "/word_list.txt", 'w')

	wordList = []
	wordCount = 0

	# While there are remaining subtitles in subtitle list
	for sub in subtitle_list:
		currWord = ""
		i = 0
		# While there are characters left in this subtitle
		while (i < len(sub.content)):
			currChar = sub.content[i]
			# If there is a (, [, {, <, any characters between them and the corresponding closing brace is disregarded
			# This handles sound effects and custom fonts
			# Emulates a do while loop for checking for ()
			if (currChar == '('):
				while True:
					i += 1
					currChar = sub.content[i]
					if (currChar == ')'):
						if (i < len(sub.content) - 1):
							i += 1
							currChar = sub.content[i]
						break

			# Emulates a do while loop for checking for []
			if (currChar == '['):
				while True:
					i += 1
					currChar = sub.content[i]
					if (currChar == ']'):
						if (i < len(sub.content) - 1):
							i += 1
							currChar = sub.content[i]
						break

			# Emulates a do while loop for checking for {}
			if (currChar == '{'):
				while True:
					i += 1
					currChar = sub.content[i]
					if (currChar == '}'):
						if (i < len(sub.content) - 1):
							i += 1
							currChar = sub.content[i]
						break

			# Emulates a do while loop for checking for <>
			if (currChar == '<'):
				while True:
					i += 1
					currChar = sub.content[i]
					if (currChar == '>'):
						if (i < len(sub.content) - 1):
							i += 1
							currChar = sub.content[i]
						break
			
			# If there is a -, the preceding word is removed if there is a " " following and no spaces have been encountered yet. 
			# Otherwise it is changed to a space
			# This handles hyphenated words and character names, removing character names and seperating hyphenated words
			if (currChar == '-'):
				if (i < len(sub.content) - 1):
					if (sub.content[i + 1] == ' '):
						currWord = ""
					else:
						currChar = " "
				else:
					currChar = "\0"
			# If there is a :, then it is maintained if the preceding and following characters are numbers
			# If there is a following space and there are no encountered spaces in the string, the preceding word is removed
			# Otherwise the : is disregarded and changed to an empty character
			# This handles times ie) 8:45 and character names. Otherwise colons are removed
			elif (currChar == ':'):
				if (i < len(sub.content) - 1) and (i != 0):
					if (sub.content[i + 1] == ' '):
						currWord = ""
						currChar = " "
					elif ((ord(sub.content[i - 1]) < 48) or (ord(sub.content[i - 1]) > 57)) or ((ord(sub.content[i + 1]) < 48) or (ord(sub.content[i + 1]) > 57)):
						currChar = "\0"
				else:
					currChar = "\0"
			# If the current character is valid, 0-9, a-z, A-Z, ', :. They are added to the current word. 
			if (ord(currChar) == 58) or (ord(currChar) == 39) or ((ord(currChar) >= 48) and (ord(currChar) <= 57)) or ((ord(currChar) >= 65) and (ord(currChar) <= 90)) or ((ord(currChar) >= 97) and (ord(currChar) <= 122)):
				currWord += currChar
			elif not ((currWord == "\0") or (currWord == "") or (currWord == " ") or (currWord == "\t")):
				# If the current character is a " " or "\n", the current word is added to the word list.
				# Current Word Count is iterated, spaceFound is set to false, the current word is set to an empty string
				if (ord(currChar) == 32) or (currChar == '\n') or (i == len(sub.content) - 1):
					wordCount += 1
					file.write(str(wordCount) + ")\t" + currWord.lower() + "\t\t" + str((sub.end).total_seconds()) + '\n')
					currWord = ""
			# Current index is iterated
			i += 1
	return (path + "/word_list.txt")


def get_word_count(word_list_path, dirname="custom"):
	"""
	Takes a path to a word_list file, determines the frequency of each word and writes results
	to the file at write_path. Sorts list
	:param1 word_list: String, path to file containing word_list. Output of get_word_list()
	"""
	path = sys.path[0] + "/../../sub_files/txt/" + dirname
	if not (os.path.isdir(path)):
		os.mkdir(path)
	word_list = load_word_list(word_list_path)
	with open(path + "/word_count.txt", 'w') as word_count:
		length = len(word_list)
		# For each element in work list
		while(len(word_list) != 0):
			searchword = word_list[0][0]
			frequency = 0
			# For i from 0 to len(work_list)
			j = 0
			while (j < length):
				# If word is desired word, pop element and incriment counter
				if (word_list[j][0] == searchword):
					word_list.pop(j)
					length = len(word_list)
					frequency = frequency + 1
				else:
					j = j + 1
			# Add word and counter to the file
			word_count.write("0)\t" +searchword + "\t\t" + str(frequency) + '\n')
	sort_word_count(path + "/word_count.txt")
	return (path + "/word_count.txt")

def sort_word_count(word_count_path):
	"""
	Takes in a file of formatted word counts, sorts the file and re-writes to same file
	:param1 word_count_path: String, path to word_count file
	"""
	word_count = load_word_count(word_count_path)

	sort_freq_list(word_count)

	with open(word_count_path, 'w') as file:
		i = 1
		for word_freq in word_count:
			file.write(str(i) + ")\t" + word_freq[0] + "\t\t" + str(word_freq[1]) + '\n')
			i += 1

def sort_freq_list(arr):
	"""
	Sorts a list of word count lists using merge sort.
	:param1 arr: A list of word count lists, used by passing path to word_count file to sort_word_count
	"""
	if len(arr) >1: 
		mid = len(arr)//2 #Finding the mid of the array 
		L_list = arr[:mid] # Dividing the array elements  
		R_list = arr[mid:] # into 2 halves 
		
		sort_freq_list(L_list) # Sorting the first half 
		sort_freq_list(R_list) # Sorting the second half 
		
		i = j = k = 0
		  
		# Copy data to temp arrays L_list[] and R_list[] 
		while i < len(L_list) and j < len(R_list): 
			if (L_list[i])[1] > (R_list[j])[1]: 
				arr[k] = L_list[i] 
				i+=1
			else: 
				arr[k] = R_list[j] 
				j+=1
			k+=1
		  
		# Checking if any element was left 
		while i < len(L_list): 
			arr[k] = L_list[i] 
			i+=1
			k+=1
		  
		while j < len(R_list): 
			arr[k] = R_list[j] 
			j+=1
			k+=1