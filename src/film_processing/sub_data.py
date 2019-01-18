#!/usr/bin/env python3

#imports
import sys
import os
import math
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(sys.path[0] + "/../")
import film_processing.film_data
import sub_processing.srt_parsing as srtp

class SubtitleData():

	def __init__(self):
		self.subpath = " "
		self.listpath = " "
		self.countpath = " "
		self.imgpath = " "

	def open_subtitle(self, subtitle_path):
		self.subpath = subtitle_path
		dirname = subtitle_path.split("/")[-2]
		word_list = srtp.load_srt(self.subpath)
		self.listpath = srtp.get_word_list(word_list, dirname)
		self.countpath = srtp.get_word_count(self.listpath, dirname)


	def get_phrase_count(self, phrase):
		"""
		Determines frequency of a multi-word phrase in a word_list file. Returns result as integer
		:param1 phrase: String, a multi-word phrase to be searched for in word_list
		:param2 word_list_path: String, path to file containing word_list. Output of get_word_list
		:returns: Integer, representing frequency of phrase's appearance in word_list file 
		"""
		phrase = phrase.lower()			# Converts phrase into lower case form
		phrase_list = phrase.split()	# Converts phrase into list of words
		word_list = srtp.load_word_list(self.listpath)	# Loads entire subtitle into word_list
		frequency = 0	# Represents the frequency of the phrase
		judge_word = 0	# Represents the word in the phrase to be looking for
	
		# For every every word in the list, check for the correct sequence of words in front
		for word in word_list:
			# If the word is equal to the desired phrase word 
			if (word[0] == phrase_list[judge_word]):
				# Begin to look for the next word in phrase
				judge_word = judge_word + 1
				# If the word to look for exceeds the length of the phrase, the phrase is found
				if (judge_word == len(phrase_list)):
					# Incriment frequency and revert word to look for to first word in phrase
					frequency = frequency + 1
					judge_word = 0
			# Otherwise, the phrase is not here. Revert to looking for first word in phrase.
			else:
				judge_word = 0
		return frequency
	
	def get_phrase_freq(self, phrase, count):
		lowerphrase = phrase.lower()
		with open(self.countpath, 'r') as file:
			while (file):
				line = file.readline().split("\t")
				word = line[1]
				if (word == lowerphrase):
					return get_nth_string(int(line[0][:-1]))
		return "0th"

	def get_phrase_count_data(self, phrase, grouping=5):
		"""
		Determines frequency of phrase in a word list file over time. Returns a dictionary with
		with multiples of grouping as minutes, and count of phrase as of that grouping
		:param1 phrase: String, a multi-word phrase to be searched for in word_list
		:param2 word_list_path: String, path to file containing word_list. Output of get_word_list
		:param3 grouping: integer, minute window to measure occurence of phrase
		:returns: Dictionary with return['time'] = [0, 1*gropuing, 2*grouping...] |
					return['count'] = [0, count_(0 - group), count_(1*group - 2*group), ...]
		"""
		count = [0]	# Create count list
		time = [0]	# Create time list
		phrase = phrase.lower()			# Converts phrase into lower case form
		phrase_list = phrase.split()	# Converts phrase into list of words
		word_list = srtp.load_word_list(self.listpath)	# Loads entire subtitle into word_list
		frequency = 0	# Represents the frequency of the phrase
		judge_word = 0	# Represents the word in the phrase to be looking for
	
		# For every every word in the list, check for the correct sequence of words in front
		for word in word_list:
			# If the word is equal to the desired phrase word 
			if (word[0] == phrase_list[judge_word]):
				# Begin to look for the next word in phrase
				judge_word = judge_word + 1
				# If the word to look for exceeds the length of the phrase, the phrase is found
				if (judge_word == len(phrase_list)):
					# Incriment frequency and revert word to look for to first word in phrase
					judge_word = 0
					if (math.floor(word[1]/60)//grouping != time[-1]):
						#time.append(math.ceil((word[1]/60)/grouping))
						time.append((math.ceil(word[1]/60)//grouping)*grouping)
						count.append(count[-1] + 1)
					else:
						count[-1] = count[-1] + 1
			# Otherwise, the phrase is not here. Revert to looking for first word in phrase.
			else:
				judge_word = 0
		return {'time' : time, 'count' : count}
	
	def get_phrase_count_plot(self, phrase, count_data, dirname="custom"):
		"""
		Creates a plot png file with given data into the sub_files/png directory
		:param1 phrase:	The phrase being searched for in subtitles
		:param2 count_data:	A dictionary object with two lists [time] and [count]
		:param3 dirname: This is the name of the directory to write the graph to. This is by default
		'custom' but when used in conjunction with subscene search, will be set to imdbid
		"""
		path = sys.path[0] + "/../../sub_files/png/" + dirname
		if not (os.path.isdir(path)):
			os.mkdir(path)
		plt.plot(count_data['time'], count_data['count'])
	
		plt.xlabel('Time (minutes)')
		plt.ylabel('Frequency')
	
		plt.title("Frequency of \"" + phrase + "\" in Film")

		plt.savefig(path + "/plot.png")
		#plt.show()
		plt.close()
		self.imgpath = (path + "/plot.png")

	def get_word_count_data(self, grouping=5):
		count = [0]	# Create count list
		time = [0]	# Create time list
		word_list = srtp.load_word_list(self.listpath)	# Loads entire subtitle into word_list
		# For every every word in the list, add one to count and time to time list
		for word in word_list:
			if (math.floor(word[1]/60)//grouping != time[-1]):
				time.append((math.ceil(word[1]/60)//grouping)*grouping)
				count.append(count[-1] + 1)
			else:
				count[-1] = count[-1] + 1
		return {'time' : time, 'count' : count}

	def get_word_count_plot(self, count_data, dirname="custom"):
		path = sys.path[0] + "/../../sub_files/png/" + dirname
		if not (os.path.isdir(path)):
			os.mkdir(path)
		plt.plot(count_data['time'], count_data['count'])
	
		plt.xlabel('Time (minutes)')
		plt.ylabel('Word Count')
	
		plt.title("Total Words in Film")

		plt.savefig(path + "/plot.png")
		#plt.show()
		plt.close()
		self.imgpath = (path + "/plot.png")

	def get_word_variety_data(self, grouping=5):
		count = [0]	# Create count list
		time = [0]	# Create time list
		word_list = srtp.load_word_list(self.listpath)	# Loads entire subtitle into word_list
		unique_words = []
		# For every every word in the list check for the unique word
		for word in word_list:
			is_unique = True
			for unique in unique_words:
				if (unique == word[0]):
					is_unique = False
					break
			if (is_unique == True):
				# Adds entry to list
				if (math.floor(word[1]/60)//grouping != time[-1]):
					time.append((math.ceil(word[1]/60)//grouping)*grouping)
					count.append(count[-1] + 1)
				else:
					count[-1] = count[-1] + 1
				unique_words.append(word[0])
		return {'time' : time, 'count' : count}

	def get_word_variety_plot(self, count_data, dirname="custom"):
		path = sys.path[0] + "/../../sub_files/png/" + dirname
		if not (os.path.isdir(path)):
			os.mkdir(path)
		plt.plot(count_data['time'], count_data['count'])
	
		plt.xlabel('Time (minutes)')
		plt.ylabel('Unique Words')
	
		plt.title("Unique Words in Film")

		plt.savefig(path + "/plot.png")
		#plt.show()
		plt.close()
		self.imgpath = (path + "/plot.png")

def get_nth_string(number):
	"""
	Finds the nth string of a number. ex) 3: 3rd 256: 256th
	:param1 number: a nonegative integer
	:returns: a string
	"""
	nth = ""
	if (number % 100 == 11):
		nth = str(number) + "th"
	elif (number % 100 == 12):
		nth = str(number) + "th"
	elif (number % 100 == 13):
		nth = str(number) + "th"
	elif (number % 10 == 1):
		nth = str(number) + "st"
	elif (number % 10 == 2):
		nth = str(number) + "nd"
	elif (number % 10 == 3):
		nth = str(number) + "rd"
	else:
		nth = str(number) + "th"
	return nth