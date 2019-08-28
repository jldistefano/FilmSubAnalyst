import sys
from math import ceil
sys.path.append(sys.path[0] + "/../")
from film_processing.film_data import get_movie_info, search_for_movie, fixIMDBurl, get_sub_files, clean_sub_dir, get_IMDB_ID
from film_processing.sub_data import SubtitleData, get_nth_string
from sub_processing.srt_parsing import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QPushButton, QAction, QLabel, QVBoxLayout, \
    QFrame, QDialog, QPlainTextEdit, QLineEdit, QTabWidget, QGroupBox, QFileDialog, QInputDialog, QMessageBox
from PyQt5.QtGui import QFont, QPalette, QPixmap
from PyQt5 import QtCore

class Gui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Subtitle Analyst v0.5'
        self.winWidth = 1040
        self.winHeight = 605
        self.initUI()

    def initUI(self):
        """
        Sets the size and elements on main dialog, and sets alternate dialogs.
        Establishes fonts to be used throughout UI.
        """
        self.setWindowTitle(self.title)
        #self.setFixedSize(self.width, self.height)
        self.setGeometry(100, 100, self.winWidth, self.winHeight)

        # Fonts to be used throughout the project
        self.bigFont = QFont("Times", 18,QFont.Bold)
        self.headerFont = QFont("Times", 15)
        self.infoFont = QFont("Arial", 10)

        # Creates subtitle object to hold subtitle data
        self.subData = SubtitleData()

        #== MAIN DIALOG =======================================================
        # Initializes Main Dialog elements
        initSubFileDir()
        self.initFileBar()
        self.initGraph()
        self.initList()
        self.initTitle()

        # Creates a main widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Creates a layout, and places gui elements on it
        # 30 Rows, 52 columns
        #gridlayout.addWidget(widget, startRow, startCol, #rows, #cols)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.progTitle, 0, 0, 1, 52)
        gridLayout.addWidget(self.listTabs, 1, 0, 30, 18)
        gridLayout.addWidget(self.graphInfo, 1, 18, 2, 34)
        gridLayout.addWidget(self.graphLabel, 3, 18, 28, 34)
        centralWidget.setLayout(gridLayout)
        # Initializes secondary dialogs
        #self.initSettingsDialog()  # Settings Dialog, currently unimplemented
        self.initMovieDialog()

    def showMovieDialog(self):
        """
        Resets the movie dialog to a default state, and shows the dialog.
        """
        # Resets and executes movie dialog
        self.resetMovieDialog()
        self.movieDialog.exec()

    def closeMovieDialog(self):
        """
        Closes the movie dialog
        """
        self.movieDialog.reject()

#    def showSettingsDialog(self):
#        """
#        Shows the settings dialog
#        """
#        self.settingsDialog.exec()

    def showPhraseDialog(self):
        """
        Shows the Phrase input dialog, uses the preset QInputDialog
        """
        #== PHRASE SEARCH DIALOG ============================================
        # This code executes the dialog in addition to creating it, stores value in 'phrase'
        phrase, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter phrase to search for:')

#    def initSettingsDialog(self):
#        """
#        Initializes the settings dialog, including the labels and buttons
#        """
#        #== SETTINGS DIALOG =================================================
#        self.settingsDialog = QDialog()
#        self.settingsDialog.setWindowTitle("Settings")
#        self.settingsDialog.setFixedSize(485, 175)
#
#        self.settingsOkButton = QPushButton("OK", self.settingsDialog)
#        self.settingsOkButton.resize(80, 30)
#        self.settingsOkButton.move(390, 30)
#
#        self.settingsCancelButton = QPushButton("Cancel", self.settingsDialog)
#        self.settingsCancelButton.resize(80, 30)
#        self.settingsCancelButton.move(390, 70)
#        self.settingsCancelButton.clicked.connect(self.settingsDialog.reject)
#
#        self.optionsGroup = QGroupBox("Options", self.settingsDialog)
#        self.optionsGroup.resize(350, 150)
#        self.optionsGroup.move(20, 10)
#
#        self.excludeLabel = QLabel("Exclude Common Words: ")
#        self.settingsGrid = QGridLayout()
        

    def initFileBar(self):
        """
        Initializes the file bar. In the format of  | FILE  | VIEW      |
                                                    | OPEN  | PHRASE    |
                                                    | SEARCH| COUNT     |
                                                    | EXIT  | VARIETY   |

        """
        # Creates a menu bar as a class object
        self.mainMenu = self.menuBar() 
        # FILE TAB ========================================================
        # Initializes File Tab
        self.fileMenu = self.mainMenu.addMenu('File')

        # Initializes Sub Tabs, including shortcuts
        self.openSubButton = QAction('Open File', self)
        self.openSubButton.setShortcut('Ctrl+O')
        self.openSubButton.triggered.connect(self.openFile)
        self.fileMenu.addAction(self.openSubButton)

        self.searchButton = QAction('Search Movies', self)
        self.searchButton.setShortcut('Ctrl+M')
        self.searchButton.triggered.connect(self.showMovieDialog)
        self.fileMenu.addAction(self.searchButton)

        self.cleanButton = QAction('Empty Files', self)
        self.cleanButton.setShortcut('Ctrl+E')
        self.cleanButton.triggered.connect(self.cleanDirectory)
        self.fileMenu.addAction(self.cleanButton)

        self.quitButton = QAction('Quit', self)
        self.quitButton.setShortcut('Ctrl+Q')
        self.quitButton.triggered.connect(self.close)
        self.fileMenu.addAction(self.quitButton)

        # VIEW TAB ========================================================
        # Initializes View Tab
        self.viewMenu = self.mainMenu.addMenu('View')

        # Initializes Sub Tabs, including shortcuts. All submenus starts disabled
        self.phraseButton = QAction('Phrase Search', self)
        self.phraseButton.setShortcut('Ctrl+F')
        self.phraseButton.triggered.connect(self.viewPhrase)
        self.phraseButton.setEnabled(False)
        self.viewMenu.addAction(self.phraseButton)

        self.countButton = QAction('Word Count', self)        
        self.countButton.triggered.connect(self.viewWordCount)
        self.countButton.setEnabled(False)
        self.viewMenu.addAction(self.countButton)

        self.varietyButton = QAction('Word Variety', self)
        self.varietyButton.triggered.connect(self.viewWordVariety)
        self.varietyButton.setEnabled(False)
        self.viewMenu.addAction(self.varietyButton)

#        # TOOLS TAB =======================================================
#        self.toolsMenu = self.mainMenu.addMenu('Tools')
#        self.helpButton = QAction('Help', self)
#        #self.helpButton.triggered.connect(#GO TO README OR GITHUB#)
#        self.helpButton.setEnabled(False)
#        self.toolsMenu.addAction(self.helpButton)
#
#        self.settingsButton = QAction('Settings', self)
#        self.settingsButton.triggered.connect(self.showSettingsDialog)
#        self.toolsMenu.addAction(self.settingsButton)

    def initGraph(self):
        """
        Initializes the graph section of the main dialog. Graph is held using a QLabel
        """
        # This label holds the image of the graph
        self.graphLabel = QLabel("", self)
        self.graphLabel.setGeometry(0, 0, 650, 650)
        self.graphLabel.setAlignment(QtCore.Qt.AlignCenter)

        # This holds information about the graph
        self.graphInfo = QLabel("", self)
        self.graphInfo.setGeometry(0, 0, 650, 60)
        self.graphInfo.setFont(self.headerFont)
        self.graphInfo.setAlignment(QtCore.Qt.AlignCenter)

    def initList(self):
        """
        Initializes the title lable, information label, and list content
        """
        # Initializes an information label for word count list
        self.countInfo = QLabel("", self)
        self.countInfo.setFont(self.infoFont)

        # Initializes an information label for word list
        self.listInfo = QLabel("", self)
        self.listInfo.setFont(self.infoFont)

        # Initializes the tab object
        self.listTabs = QTabWidget(self)
        self.listTabs.setGeometry(0, 0, 355, 521)
        self.listTabs.setMinimumWidth(355)
        self.listTabs.setVisible(False)

        # Initializes a box to load raw subtitle files
        self.subRawContent = QPlainTextEdit(self)
        self.subRawContent.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.subRawContent.setReadOnly(True)

        # Initializes a box to load word count data
        self.wordCountContent = QPlainTextEdit(self)
        self.wordCountContent.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.wordCountContent.setReadOnly(True)

        # Initializes a box to load word list data
        self.wordListContent = QPlainTextEdit(self)
        self.wordListContent.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.wordListContent.setReadOnly(True)

        countLayout = QVBoxLayout()
        countLayout.addWidget(self.countInfo)
        countLayout.addWidget(self.wordCountContent)

        wordsLayout = QVBoxLayout()
        wordsLayout.addWidget(self.listInfo)
        wordsLayout.addWidget(self.wordListContent)

        countFrame = QFrame(self)
        countFrame.setLayout(countLayout)
        wordsFrame = QFrame(self)
        wordsFrame.setLayout(wordsLayout)

        self.listTabs.addTab(self.subRawContent, "Raw Subtitle")
        self.listTabs.addTab(wordsFrame, "Word List")
        self.listTabs.addTab(countFrame, "Word Count")

    def initTitle(self):
        """
        Initializes the title for the main dialog
        """
        # This variable holds the title
        self.movieTitle = ""
        # Creates a Label for the main dialog title
        self.progTitle = QLabel("No Subtitle Loaded", self)
        self.progTitle.setGeometry(0, 0, 1000, 27)
        self.progTitle.setFont(self.bigFont)

    def resetUI(self):
        self.movieTitle = ""
        # Creates a Label for the main dialog title
        self.progTitle.setText("No Subtitle Loaded")

        self.countInfo.setText("")
        self.listInfo.setText("")
        self.subRawContent.setPlainText("")
        self.wordCountContent.setPlainText("")
        self.wordListContent.setPlainText("")
        self.listTabs.setVisible(False)
        self.graphLabel.setVisible(False)
        self.graphInfo.setVisible(False)

        # Creates subtitle object to hold subtitle data
        self.subData = SubtitleData()

    def cleanDirectory(self):
        self.resetUI()
        clean_sub_dir()

    def setGraph(self, filename, info):
        """
        Sets the graph label to a given image file, and sets the grpah info to a given string
        :param filename: string, represents filepath to an image file
        :param info: string, represents information about the graph
        """
        # Creates a pixmap with a given image file, sets the pixmap of the label to the pixmap
        self.graph = QPixmap(filename).scaledToWidth(650)
        self.graphLabel.setPixmap(self.graph)
        self.graphLabel.setVisible(True)

        # Sets the text of the graph info to given string
        self.graphInfo.setText(info)
        self.graphInfo.setVisible(True)

    def setList(self, filename, info, scrollBox, infoBox):
        """
        Sets the list title and info labels, and list content QLineEdit object to given strings and filename
        :param filename: string, represents the filepath to a text file
        :param info: string, represents labels for list columns
        """
        listcontent = open(filename, 'r', encoding= "latin-1").read()

        scrollBox.setVisible(True)
        scrollBox.setPlainText(listcontent)
        infoBox.setText(info)

    def setTitle(self, title):
        """
        Sets the title of main window to user input
        :param title: string, represents title for main window
        """
        self.progTitle.setText(title)

    def openFile(self):
        """
        Opens a file search dialog using the preset QFileDialog. Used to open .srt files
        """
        # Opens a File Search Dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open a Subtitle File","../../sub_files/srt","Subtitle Files (*.srt);;All Files (*)", options=options)
        if (fileName):
            # Attempts to open a file
            try:
                # Sets the subData to data held in selected file
                self.subData.open_subtitle(fileName)
                # Sets movieTitle to name up subtitle file, up to 33 characters
                self.movieTitle = fileName.split("/")[-1]
                if (len(self.movieTitle) > 43):
                    self.movieTitle = fileName.split("/")[-1][0:40] + "..."

                # Sets the title of the main dialog
                self.setTitle("Subtitle for \"" + self.movieTitle + "\" opened")

                # Sets List to raw subtitle text
                self.setList(self.subData.subpath, " ", self.subRawContent, self.countInfo)
                # Load word_count.txt to list
                self.setList(self.subData.countpath, "# Frequency   Word                                    # Occurences", self.wordCountContent, self.countInfo)
                # Load word_list.txt to list
                self.setList(self.subData.listpath, "# Word            Word                                    Time (seconds)", self.wordListContent, self.listInfo)
                self.listTabs.setCurrentIndex(0)
                self.listTabs.setVisible(True)

                # If a file is opened, the subtabs in the view tab become enabled. The main dialog elements become visible
                self.phraseButton.setEnabled(True)
                self.countButton.setEnabled(True)
                self.varietyButton.setEnabled(True)
                self.graphLabel.setVisible(False)
                self.graphInfo.setVisible(False)
            # If file cannot be opened, an error window is created
            except:
                print("Subtitle File Could Not Be Opened") # Change to warning dialog
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Subtitle File Could Not Be Opened")
                msg.setWindowTitle("Error")
                msg.exec()

    def viewPhrase(self):
        """
        Opens a phrase search dialog, using the preset QInputDialog. Dialog is used to get
        a search phrase from user input.
        """
        # Open Search Dialog
        phrase, ok = QInputDialog.getText(self, "Phrase Search", "Enter a Search Phrase: ")

        if ok:    
            # Use Phrase to Generate Graph and Graph Info
            count_data = self.subData.get_phrase_count_data(phrase.lower(), .1)
            dirname = self.subData.listpath.split("/")[-2]
            self.subData.get_phrase_count_plot(phrase, count_data, dirname)
            # If the phrase is found in the film, change the list, title and graph
            if (count_data['count'][-1] != 0):
                info = str(count_data['count'][-1]) + " Instances Of \"" + phrase + "\" In This Film\n"
                if (len(phrase.split()) == 1):
                    info += "\"" + phrase + "\" Is The " + self.subData.get_phrase_freq(phrase, count_data['count'][-1]) + " Most Common Word In This Film"
                self.setGraph(self.subData.imgpath, info)
                self.setTitle("Phrase Search In \"" + self.movieTitle + "\"")
            # Otherwise create a warning dialog
            else:
                print("Phrase \"" + phrase + "\" not found") # Change to warning dialog
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Phrase \"" + phrase + "\" not found")
                msg.setWindowTitle("Error")
                msg.exec()

    def viewWordCount(self):
        """
        Gets the data about the word count from a loaded subtitle file, sets list and graph
        to word list and a word count over time graph. Graph information includes total words and words per minute
        """
        # Use Phrase to Generate Graph and Graph Info
        count_data = self.subData.get_word_count_data(.1)
        dirname = self.subData.listpath.split("/")[-2]
        self.subData.get_word_count_plot(count_data, dirname)
        # If the phrase is found in the film, change the list, title and graph
        if (count_data['count'][-1] != 0):
            info = "There's " + "{:,}".format(count_data['count'][-1]) + " Total Words In This Film \n"
            info += "That's {:.2f}".format((count_data['count'][-1])/(count_data['time'][-1])) + " Words per Minute or About "
            wps = math.ceil(((count_data['count'][-1])/(count_data['time'][-1])) / 60)
            if (wps == 1):
                info += "1 Word per Second"
            else:
                info += str(wps) + " Words per Second"

            self.setGraph(self.subData.imgpath, info)
            self.setTitle("Total Word Count In \"" + self.movieTitle + "\"")
        # If word count is zero, an error message is opened
        else:
            print("There are no words in this film")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("There are no words in this film")
            msg.setWindowTitle("Error")
            msg.exec()

    def viewWordVariety(self):
        """
        Gets the data about the word variety from a loaded subtitle file, sets list and graph
        to word list and a unique words over time graph. Graph information includes total unique words and new words per minute
        """
        # Use Phrase to Generate Graph and Graph Info
        count_data = self.subData.get_word_variety_data(1/60)
        dirname = self.subData.listpath.split("/")[-2]
        self.subData.get_word_variety_plot(count_data, dirname)
        # If the phrase is found in the film, change the list, title and graph
        if (count_data['count'][-1] != 0):
            info = "There's " + "{:,}".format(count_data['count'][-1]) + " Total Unique Words In This Film \n"
            info += "That's {:.2f}".format(math.ceil((count_data['count'][-1])/(count_data['time'][-1]))) + " New Words per Minute"
            self.setGraph(self.subData.imgpath, info)
            self.setTitle("Total Unique Word Count In \"" + self.movieTitle + "\"")
        # If the word count is zero, an error message is opened
        else:
            print("There are no words in this film")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("There are no words in this film")
            msg.setWindowTitle("Error")
            msg.exec()

    def initMovieDialog(self):
        """
        Creates a dialog to search for movies, and download their subtitles. 
        """
        #== MOVIE SEARCH DIALOG =============================================
        # Initializes Dialog, and its title and size
        self.movieDialog = QDialog()
        self.movieDialog.setWindowTitle("Film Search")
        self.movieDialog.setFixedSize(425, 300)

        # Initializes title label for search box
        self.searchLabel = QLabel("Search for a movie: ", self.movieDialog)
        self.searchLabel.setGeometry(0, 0, 200, 25)
        self.searchLabel.move(18, 10)

        # Initializes search text box
        self.searchBox = QLineEdit(self.movieDialog)
        self.searchBox.resize(300, 30)
        self.searchBox.move(18, 35)

        # Initializes search button
        self.searchButton = QPushButton("Search", self.movieDialog)
        self.searchButton.resize(80, 30)
        self.searchButton.move(330, 35)
        self.searchButton.clicked.connect(self.searchMovie)

        # Initializes ok button
        self.searchOkButton = QPushButton("OK", self.movieDialog)
        self.searchOkButton.resize(80, 30)
        self.searchOkButton.move(330, 90)
        self.searchOkButton.clicked.connect(self.getSubtitle)
        self.searchOkButton.setEnabled(False)

        # Initializes cancel button
        self.searchCancelButton = QPushButton("Cancel", self.movieDialog)
        self.searchCancelButton.resize(80, 30)
        self.searchCancelButton.move(330, 130)
        self.searchCancelButton.clicked.connect(self.movieDialog.reject)

        # Initializes Group Box for movie information
        self.infoGroup = QGroupBox("Movie Info", self.movieDialog)
        self.infoGroup.resize(300, 215)
        self.infoGroup.move(18, 70)

        # Initializes labels for movie information
        self.nameLabel = QLabel("Title: ")
        self.yearLabel = QLabel("Year: ")
        self.dirLabel = QLabel("Director: ")
        self.castLabel = QLabel("Cast: ")
        self.runLabel = QLabel("Runtime: ")
        self.imdbLabel = QLabel("IMDB: ")
        self.imdbLabel.linkActivated.connect(self.link)

        # Creates a grid layout, and places information labels within
        self.infoGrid = QGridLayout()
        self.infoGrid.addWidget(self.nameLabel, 0, 0)
        self.infoGrid.addWidget(self.yearLabel, 1, 0)
        self.infoGrid.addWidget(self.dirLabel, 2, 0)
        self.infoGrid.addWidget(self.castLabel, 3, 0)
        self.infoGrid.addWidget(self.runLabel, 4, 0)
        self.infoGrid.addWidget(self.imdbLabel, 5, 0)
        self.infoGroup.setLayout(self.infoGrid)

    def resetMovieDialog(self):
        """
        Sets the elements in the movie dialog to their default positions
        """
        # Sets buttons back to default positions
        self.searchButton.setEnabled(True)
        self.searchOkButton.setEnabled(False)
        # Empties text from text box
        self.searchBox.setText("")
        # Resets labels to default content
        self.nameLabel.setText("")
        self.yearLabel.setText("")
        self.dirLabel.setText("")
        self.castLabel.setText("")
        self.runLabel.setText("")
        self.imdbLabel.setText("")

    def searchMovie(self):
        """
        Searches for a movie using user input. Sets movie information to ? until found.
        Finds information from IMDB, if imdb cannot be used movie info is found from subtitle.
        This is triggered when SEARCH button is pressed.
        """
        # Disables search button
        self.searchButton.setEnabled(False)
        self.searchOkButton.setEnabled(False)
        # Collects user input string
        search_text = self.searchBox.text()

        # Sets all movie info labels to ?
        self.nameLabel.setText("Title: ?")
        self.yearLabel.setText("Year: ?")
        self.dirLabel.setText("Director: ?")
        self.castLabel.setText("Cast: ?")
        self.runLabel.setText("Runtime: ?")
        self.imdbLabel.setText("IMDB URL: ?")
        # Attempts to gather movie subscene
        try:
            self.subscene_info = search_for_movie(search_text)
        # If unsuccessful, subscene_info is set to none
        except:
            self.subscene_info = None
        # If successful imdb info is attempted to be found
        if (self.subscene_info is not None):
            # Fixes the imdb url, as subscene movie information often includes a broken imdb url
            self.subscene_info['url'] = fixIMDBurl(self.subscene_info['url'])
            # Attempts to get the imdb info about a film
            try:
                # Collects imdb info about the movie using the url from subscene
                imdb_info = get_movie_info(self.subscene_info['url'])
                # Sets the movie info labels to imdb info
                self.nameLabel.setText("Title: " + imdb_info['title'])
                self.yearLabel.setText("Year: " + imdb_info['year'])
                self.dirLabel.setText("Director: " + imdb_info['director'])
                self.castLabel.setText("Cast: " + imdb_info['cast'])
                self.runLabel.setText("Runtime: " + imdb_info['runtime'])
                self.imdbLabel.setText('<a href=\"' + self.subscene_info['url'] + '\">IMDB</a>')
                # Re-enables OK Button
                self.searchOkButton.setEnabled(True)
            # If unsuccessful, movie info is pulled from subscene
            except:
                print("IMDB Info could not be found")
                # Sets movie info labels to subscene info 
                self.nameLabel.setText("Title: " + self.subscene_info['title'])
                self.yearLabel.setText("Year: " + str(self.subscene_info['year']))
                self.dirLabel.setText("All IMDB Information Could Not Be Found")
                self.castLabel.setText("")
                self.runLabel.setText("")
                self.imdbLabel.setText('<a href=\"' + self.subscene_info['url'] + '\">IMDB</a>')
                # Re-enables OK Button
                self.searchOkButton.setEnabled(True)
        # If subscene info could not be found, error message is pulled
        else:
            print("Film could not be found")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Film could not be found")
            msg.setWindowTitle("Error")
            msg.exec()
        self.searchButton.setEnabled(True)

    def link(self, linkStr):
        """
        This function opens a given url in the default browser.
        :param linkStr: string, represents IMDB url
        """
        QDesktopServices.openUrl(QUrl(linkStr))

    def getSubtitle(self):
        """
        Attempts to download subtitle file from title. This is triggered when the OK button
        is clicked. It also closes the search dialog and loads the subtitle file
        """
        # Sets movie title to subscene gathered title
        self.movieTitle = self.subscene_info['title']
        # Attempts to download subtitle file
        try:
            get_sub_files(self.movieTitle)
        # If download fails, warning dialog is opened
        except (AppError) as error:
            print("Subtitle Download Failed")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Subtitle Download Failed")
            msg.setWindowTitle("Error")
            msg.exec()
        self.closeMovieDialog()
        self.openSearchFile()

    def openSearchFile(self):
        """
        Opens the directory of downloaded subtitle files. After file is opened, subtitle
        is loaded to subData file. 
        """
        srtpath = "../../sub_files/srt/" + get_IMDB_ID(self.subscene_info['url'])
        # Opens a File Search Dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open a Subtitle File",srtpath,"Subtitle Files (*.srt);;All Files (*)", options=options)
        if (fileName):
            # Attempts to open the subtitle file
            try:
                # Sets the subData to data held in selected file
                self.subData.open_subtitle(fileName)
                self.listTabs.setVisible(False)
                # Sets List to raw subtitle text
                self.setList(self.subData.subpath, " ", self.subRawContent, self.countInfo)
                # Load word_count.txt to list
                self.setList(self.subData.countpath, "# Frequency   Word                                    # Occurences", self.wordCountContent, self.countInfo)
                # Load word_list.txt to list
                self.setList(self.subData.listpath, "# Word            Word                                    Time (seconds)", self.wordListContent, self.listInfo)
                self.listTabs.setCurrentIndex(0)
                self.listTabs.setVisible(True)

                # Sets main dialog title
                self.setTitle("Subtitle for \"" + self.movieTitle + "\" opened")
                # Enables view tab buttons, and makes the graph invisible
                self.phraseButton.setEnabled(True)
                self.countButton.setEnabled(True)
                self.varietyButton.setEnabled(True)
                self.graphLabel.setVisible(False)
                self.graphInfo.setVisible(False)
            # If unsuccessful, error message is created
            except:
                print("Subtitle File Could Not Be Opened") # Change to warning dialog
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Subtitle File Could Not Be Opened")
                msg.setWindowTitle("Error")
                msg.exec()

def initSubFileDir():
    """
    Initializes the 'sub_files' directories if they do not currently exist
    """
    if not (os.path.isdir("../../sub_files")):
        os.mkdir("../../sub_files")
    if not (os.path.isdir("../../sub_files/srt")):
        os.mkdir("../../sub_files/srt")
    if not (os.path.isdir("../../sub_files/txt")):
        os.mkdir("../../sub_files/txt")
    if not (os.path.isdir("../../sub_files/png")):
        os.mkdir("../../sub_files/png")
    if not (os.path.isdir("../../sub_files/zip")):
        os.mkdir("../../sub_files/zip")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())