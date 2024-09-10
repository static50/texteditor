import curses
import time 

class screen:
    newselect = 0 # stays the same across class instances so we know which buffer we're currently updating
    
    def __init__(self, fileobjects, select, stdscr):
        self.file_obj = fileobjects[select]
        self.file_buffer = fileobjects[select].buffer
        self.rows, self.cols = stdscr.getmaxyx()
        self.y, self.x = 0, 0
        self.save = False
        self.select = select
        self.prev_x = 0 
        stdscr.nodelay(True)
        
    def checkbounds(self, axis, is_positive_direction=True):
        if axis == 'y':
            if is_positive_direction:
                return self.y < self.rows - 1
            else:
                return self.y > 0
        elif axis == 'x':
            if is_positive_direction:
                return self.x < self.cols - 1
            else:
                return self.x > 0
        return False 
                
    def calculate_index(self):
        newline = 0
        index = 0
        counted = 0
        for counted, ch in enumerate(self.file_buffer):
            if ch == '\n':
                newline += 1
                counted += 1 
            if newline == self.y:
                index = counted + self.x
                break
            
        return counted, index  
   
    def updateUI(self, stdscr):
        pass
        
    def updatescreen(self, stdscr, fileobjects, select):
        try:
            key = stdscr.getch()
        except:
            key = None
        
        
        
        if key == curses.KEY_UP and self.checkbounds('y', False):
            # self.cursorup()
            self.y -= 1
            
        if key == curses.KEY_DOWN and self.checkbounds('y', True):
            self.cursordown()
            
        if key == curses.KEY_LEFT and self.checkbounds('x', False):
            self.x -= 1
            self.prev_x = self.x
            
        if key == curses.KEY_RIGHT and self.checkbounds('x', True):
            self.x += 1
            self.prev_x = self.x
            
        if 32 < key <= 126:
            self.editbuffer(stdscr, key, True)
            
        if key == curses.KEY_BACKSPACE or key == 127:
            self.editbuffer(stdscr, key, False)
            
        if key == curses.KEY_ENTER or key == 10:
            self.editbuffer(stdscr, '\n', True)
            
            
            
        if key == 32:
            self.editbuffer(stdscr, ' ', True)
            
        if key == 9: # tab key 
            for i in range(4):
                self.editbuffer(stdscr, ' ', True)
                
        if key == 19: # ctrl+s
            # save the file
            self.save = True
            self.file_obj.savefile(self.file_obj.file, self.file_buffer)
            
        if key == 27:
            if screen.newselect > 0: 
                screen.newselect -= 1 
                return True, screen.newselect

        if key == 29:
            if screen.newselect < len(fileobjects) - 1:
                screen.newselect += 1 
                return True, screen.newselect
                
        counted, index = self.calculate_index() 
       
        stdscr.erase()

        
        stdscr.addstr(0, 0, ''.join(self.file_buffer))
        
        
        if self.save:
            stdscr.addstr(self.rows - 1, 10, " File {} saved ".format(self.file_obj.file_name))
            self.save = False
            time.sleep(0.5)
            
        stdscr.addstr(self.rows-3, 1, "index: {} maximum index: {} buffer: {}".format(index, len(self.file_buffer), self.file_buffer))
        stdscr.addstr(self.y, self.x, "")
        stdscr.refresh()
        return True, self.select
    
    def append(self, stdscr, key):
        counted, index = self.calculate_index()

        try:
            self.file_buffer = self.file_buffer[:index] + [chr(key)] + self.file_buffer[index:]
        except:
            self.file_buffer = self.file_buffer[:index] + [key] + self.file_buffer[index:]

        if key == '\n': 
            self.y += 1
            self.x = 0      
            if index == len(self.file_buffer):
                self.file_buffer = self.file_buffer[:index] + [chr('\n')] + [chr('\n')] + self.file_buffer[index:]    
                
        elif self.checkbounds('x', True): # if this fails, it means that the user is writing a line longer than the terminal width
            self.x += 1
            
    def get_prev_line_length(self):
        counted, index = self.calculate_index()
        i = (index - self.x) - 2 # index - 1 is the newline, index - 2 is the character next to it
        count = 0 
        
        while True:
            if self.file_buffer[i] == '\n':
                return count
                break
            count += 1
            i -= 1 # traverse the list in reverse
            
    def get_next_line_length(self):
        self.x = 0
        self.y += 1 
        count = 0 
        counted, index = self.calculate_index()
        if index == len(self.file_buffer):
            self.y -= 0 
            return 0
            
        for i in range(index, len(self.file_buffer)):
            if self.file_buffer[i] == '\n':
                self.x = self.prev_x
                return count
            count += 1
        self.x = self.prev_x
        return 0
        
    def cursorup(self):
        prev_line_length = self.get_prev_line_length()
        
        if not self.get_prev_line_length():
              pass 
              
        if prev_line_length < self.x:
            self.x = prev_line_length
            
        return 

    def cursordown(self):
        next_line_length = self.get_next_line_length()
        
        if next_line_length < self.x:
            self.x = next_line_length          
        else:
            self.x = self.prev_x
        return
        
    def cursor_to_prev_line(self):
        counted, index = self.calculate_index()
        newline_on_prev_line = index - 1
        
        self.x = self.get_prev_line_length()
        
        del self.file_buffer[newline_on_prev_line] # delete the newline
        self.y -= 1
        
    def removelastchar(self, stdscr):
        counted, index = self.calculate_index()
        newline_on_prev_line = index - 1
        
        if self.checkbounds('x', False): # if the user is not deleting at the beginning of a line
            del self.file_buffer[newline_on_prev_line]
            self.x -= 1
        else:
            try:
                if self.file_buffer[newline_on_prev_line] == '\n':     
                    # go back to the end of the previous line
                    self.cursor_to_prev_line() 
            except:
                pass
                
    def editbuffer(self, stdscr, key, append):        
        if append:
            self.append(stdscr, key)      
        else:  
            self.removelastchar(stdscr)

# cursor algorithm
"""
store last column position of the column 
if key is down/up
    cursor is brought to the end of the next line if the next line is shorter to or equal to the last line
    if not, the cursor is brought to the last cursor position

if key == curses.up:
    last_column_pos = self.x
    if (length_of_next_line() <= current_line)
        

if key is left or right:
    update the column position unless the cursor is already at the end of the line then
    move the cursor to the start of the nextline  
"""

# how to implement left/right up/down scrolling
"""
get the buffer dimensions:
    count rows in self.file_buffer by counting all the newlines
    count columns in self.file_buffer by counting the longest line 

set the window size 

"""
