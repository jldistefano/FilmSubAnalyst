#!/usr/bin/env python3

#imports
import sys
import os 								# Used for writing and removing zip files
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import imdb 							# Used for gathering information about films, year, title, director, and runtime
from imdb.Movie import Movie
from imdb.Person import Person
import shutil
# from imdb.helpers import get_byURL 	# Allows for access to IMDB Objects through imdb url, currently unused
import zipfile 							# Used for unzipping downloaded zip files from subscene
from subscene.subscene import search 	# Used for collceting zip files containing subtitles from subscene.com
import cfscrape							# Used for bypassing subscene.com Clouflare DDOS protection

#IMDB FUNCTIONS
def search_movie(searchMovie):
	"""
	This function searches for a film based on user inpu, and outputs
	the movie object of the first result

	:param1 searchMovie: an string, user inputted search key for a film
	:returns: a movie object, the first result by searching IMDb with searchMovie
	"""
	ia = imdb.IMDb()
	movies = ia.search_movie(searchMovie)
	return movies[0]

def get_IMDB_ID(url):
	"""
	This function returns the imdb id of a movie object

	:param1 url: URL to IMDb page, https://www.imdb.com/title/tt[IMDbID]
	:returns: string representing IMDb id in form '######'
	"""
	sections = url.split("/")
	imdbid = sections[-1][2:]
	return imdbid

def fixIMDBurl(url):
    split_url = url.split("/")
    split_id = split_url[-1]
    if (len(split_id) == 9):
        return url
    else:
        while(len(split_id) != 9):
            split_id = split_id[:2] + "0" + split_id[2:]
        new_url = ""
        for i in range(len(split_url) - 1):
            new_url += split_url[i] + "/"
        new_url += split_id
        return new_url

def get_movie_info(url):
	"""
	This function takes in a movie object and returns several pieces
	of information about the movie

	:param1 url: imdb url of movie
	:returns: Title, Release Year, Director, Runtime, ... as strings
	""" 
	ia = imdb.IMDb()
	movie = ia.get_movie(get_IMDB_ID(fixIMDBurl(url)))
	ia.update(movie)
	return {
        'title': movie['title'],
        'year': str(movie['year']) ,
        'director': str(movie['director'][0]['name']),
        'cast' : str(movie['cast'][0]['name']) + ", " + str(movie['cast'][1]['name']) + ", " + str(movie['cast'][2]['name']),
        'runtime': str(movie['runtime'])
    }

# SUBSCENE FUNCTIONS
def search_for_movie(searchMovie, language="english"):
	"""
	Searches for a movie on subspace, returns information about the film for user checking
	:param1 searchMovie: String representing search term for movie
	:returns: dictionary containing title, year, and url
	"""
	film = search(searchMovie, language)
	if film is None:
		# Last paramater dictates type of search, close search. see subscene.py
		film = search(searchMovie, language, 4)
	if film is None:
		# Last paramater dictates type of search, popular search. see subscene.py
		film = search(searchMovie, language, 3)
	if film is None:
		return film
	else:
		return {
	        'title': film.title,
	        'year': film.year,
	        'subtitles': film.subtitles,
	        'url': film.imdb
	    }

def get_lang_from_url(url):
	"""
	Subscene urls in format https://subscene.com/subtitles/[MOVIE TITLE]/[LANGAUGE]/[NUMBER]
	Access [LANGUAGE] element from url
	:param1 url: Subscene url in format https://subscene.com/subtitles/[MOVIE TITLE]/[LANGAUGE]/[NUMBER]
	:returns: String representing language of subtitle
	"""
	i = 33	# [MOVIE TITLE] starts at 32nd character of url
	language = ""
	s_count = 0	# slash count, incriments when slash is encountered
	# Adds characters between first and second slashes to language string
	while s_count < 2:
		if (url[i] == '/'):
			s_count += 1
		else:
			if (s_count == 1):
				language = language + url[i]
		i += 1
	return language

def find_download_subtitle(subtitles, language="english", title="MOVIE"):
	"""
	Finds a subtitle file in language from imdb url and downloads it to ./../sub_files
	:param1 subtitles: list of Subtitle objects from subscene
	:param2 language: desired language of subtitle, default english
	:param3 title: title of film, used for filepath
	:returns: index in subtitle list of downloaded subtitle, -1 if failed
	"""
	downloaded = False
	i = 0
	while not downloaded:
		i += 1
		if (get_lang_from_url(subtitles[i].url) == language):
			downloaded = True
	if (downloaded):
		scraper = cfscrape.create_scraper()
		url = subtitles[i].zipped_url
		r = scraper.get(url)
		path = './../../sub_files/zip/' + title + '_sub.zip'
		with open(path, 'wb') as f:
			f.write(r.content)
		return i
	return -1

def unzip_file(path, num="0000000"):
	"""
	Unzips downloaded subtitle file, renames subtitle file accordingly
	:param1 path: string path to zip flie
	:param2 num: string 00000 by default, imdid id of a file
	:returns: Dictionary object to paths to srt directory, path to word list text file, and path to word count text file
	"""
	zippo = zipfile.ZipFile(path, 'r')
	zippo.extractall("./../../sub_files/srt/" + num + "/")
	zippo.close()

def get_sub_files(searchMovie, language="english"):
	"""
	Finds and downloads a subtitle file using the searchMovie and language, default english
	:param1 searchMovie: string representing title of movie to search for
	:param2 language: string representing desired language of subtitle
	"""
	info = search_for_movie(searchMovie, language)
	i = find_download_subtitle(info['subtitles'], language, info['title'])
	if (i == -1):
		raise AppError('Searched Movie \"' + searchMovie + '\" Failed to Download.')
	else:
		path_dict = unzip_file("./../../sub_files/zip/" + info['title'] + "_sub.zip", get_IMDB_ID(fixIMDBurl(info['url'])))
		os.remove("./../../sub_files/zip/" + info['title'] + "_sub.zip")

def clean_sub_dir():
	for dirname in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/srt"):
		shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/srt/" + dirname)
	for dirname in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/txt"):
		shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/txt/" + dirname)
	for dirname in os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/png"):
		shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + "/../../sub_files/png/" + dirname)