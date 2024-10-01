import curses 
import json

class SyntaxHighlight:
    # CLASS METHODS
    def __init__(lang):
        self.set_theme()
        # keywords = get_keywords(lang) 
        keywords = []
        self.file_buffer = None

    def get_buffer():
        return self.file_buffer 

    def set_buffer(file_buffer):
        self.file_buffer = file_buffer

    # THEME METHODS 
    def set_theme(self):
        pass

    def readjson(self)
        file = open("theme.json", r)
        file.read()
        theme = json.loads(file)

    def apply_highlighting_line(self, line):
        pass

    # ALGORITHM METHODS 
    def character_front(self, start_index, end_index, char) -> bool:
        if self.is_keyword(start_index, end_index): 
            isvalid = self.is_valid_char(start_index, end_index, char)
            return self.file_buffer[start_index:end_index+1] == char and isvalid
        else:
            return -1 

    def character_back(self, start_index, end_index, char) -> bool:
        if self.is_keyword(start_index, end_index):
            return self.file_buffer[start_index-1:end_index] == char:
        else:
            return -1

    # HELPER ALGORITHM METHODS
    def is_valid_char(start_index, end_index, char):
        keyword = self.file_buffer[start_index:end_index] 
        
    def is_keyword(self, start_index, end_index): -> bool:
        return self.file_buffer[start_index:end_index] in keywords 

       
