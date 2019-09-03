import srt
import os
import sys
import sqlite3
from sqlite3 import Error
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
	Converts a word_db file, output from gen_word_db(), into a list of 
	words and second of appearance. [[word_1, time_1], [word_1, time_1], ...]
	Word # i = word_list[i][0]
	Word # i time of appearance = word_list[i][0] seconds
	:param1 path: String, path to file containing word_db. Output of gen_word_db()
	:returns: A list of lists of a word and it's time of appearance, as formatted above
	"""
	word_list = []
	# Attempt to open database file
	try:
		conn = sqlite3.connect(path)
	except:
		return

	c = conn.cursor()

	# Add each word and time into list
	for row in c.execute('''SELECT * FROM words ORDER BY tstamp'''):
		word_list.append([row[0], row[2]])

	# Save and Quit database file
	conn.commit()
	conn.close()
	return word_list

def load_word_count(path):
	"""
	Converts a word_db file, output from gen_word_db(), into a list of 
	word's and frequency. [[word_most_freq, frequency], ... , [word_least_freq, frequency]]
	nth most frequent word = word_count[n][0]
	nth frequent word number of appearances = word_count[n][1]
	:param1 path: String, path to file containing word_db. Output of gen_word_db()
	:returns: A list of lists of a word and it's time of appearance, as formatted above
	"""
	word_count = []
	# Attempt to open database file
	try:
		conn = sqlite3.connect(path)
	except:
		return

	c = conn.cursor()

	# Add each word and count into list
	for row in c.execute('''SELECT * FROM wordcount ORDER BY count DESC'''):
		word_count.append([row[0], row[1]])

	# Save and Quit database file
	conn.commit()
	conn.close()
	return word_count

def gen_word_db(subtitle_list, dirname="custom"):
	"""
	Converts a subtitle list into a sql database with two tables
	One lists words in their order of appearance with timestamps
	One lists words by their frequency
	:param1 subtitle_list: A list of subtitles, output from load_srt()
	:param2 dirname: Name of folder to store db files in, default to "custom"
	:returns: Path to database file
	"""

	path = sys.path[0] + "/../../sub_files/db/" + dirname
	if not (os.path.isdir(path)):
		os.mkdir(path)
	
	# Create the database file
	try:
		conn = sqlite3.connect(path + "/words.db")
	except:
		return

	
	c = conn.cursor()
	
	# Delete tables if they already exist
	c.execute('''DROP TABLE IF EXISTS words''')
	c.execute('''DROP TABLE IF EXISTS wordcount''')

	# Create words table
	c.execute('''CREATE TABLE words 
		(word text, ordering int, tstamp real)''')

	# Create word count table
	c.execute('''CREATE TABLE wordcount
		(word text, count int)''')

	# Add all words to word table

	# Holds the order of the words
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
					# Create tuple of values and insert into table
					values = (currWord.lower(), wordCount, (sub.end).total_seconds())
					try:
						c.execute("INSERT INTO words (word, ordering, tstamp) VALUES (?, ?, ?)", values)
					except Error as e:
						print(e)
					# Reset current word to empty
					currWord = ""
			# Current index is iterated
			i += 1

	# Generate word count table
	word_table = c.execute('''SELECT word FROM words ORDER BY word''')
	# countedWords holds the frequency of each word
	countedWords = 0
	# activeWord is the word currently being observed
	activeWord = (c.fetchone())[0]
	# countWord is used to compare with activeWord to ensure the correct word is being counted
	countWord = activeWord
	# This cursor is created so the table can both be observed and added to within the same loop
	command = conn.cursor()

	# Cycle through every row in the table
	for row in word_table:
		# Incriment count
		countedWords += 1
		# activeWord is the word within this row of the table
		activeWord = row[0]
		# If the activeWord does not match the countWord then a new word has been encountered
		if (activeWord != countWord):
			# Add the current word and its count to the table
			values = (countWord, countedWords)
			command.execute('''INSERT INTO wordcount (word, count) VALUES(?, ?)''', values)
			# Update countWord
			countWord = activeWord
			countedWords = 0

	# Save and Quit database file
	conn.commit()
	conn.close()

	# Return path to database file
	return (path + "/words.db")