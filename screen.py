import curses
import time 

class screen:
    newselect = 0 # stays the same across class instances so we know which buffer we're currently updating
    
    def __init__(self, fileobjects, select, stdscr):
        self.file_obj = fileobjects[select]
        self.file_buffer = fileobjects[select].buffer
        self.rows, self.cols  = stdscr.getmaxyx()
        self.rows -= 1 
        self.cols -= 1 
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
            self.cursorup(stdscr)
            
        if key == curses.KEY_DOWN and self.checkbounds('y', True):
            self.cursordown()
            
        if key == curses.KEY_LEFT and self.checkbounds('x', False):
            self.cursorleft()
            
        if key == curses.KEY_RIGHT and self.checkbounds('x', True):
            self.cursorright()
            
        if 32 < key <= 126:
            self.editbuffer(stdscr, key, True)
            
        if key == curses.KEY_BACKSPACE or key == 127:
            self.editbuffer(stdscr, key, False)
            
        if key == curses.KEY_ENTER or key == 10:
            self.editbuffer(stdscr, '\n', True)
            
            
            
        if key == 32: # space bar 
            self.editbuffer(stdscr, ' ', True)
            
        if key == 9: # tab key 
            for i in range(4):
                self.editbuffer(stdscr, ' ', True)
                
        if key == 19: # ctrl+s
            # save the file
            self.save = True
            self.file_obj.savefile(self.file_obj.file, self.file_buffer)
            
        if key == 27: # [ key
            if screen.newselect > 0: 
                screen.newselect -= 1 
                return True, screen.newselect

        if key == 29: # ] key 
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
            
        stdscr.addstr(self.rows-10, 1, "buffer: {}".format(self.file_buffer))
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
        elif self.checkbounds('x', True): # if this fails, it means that the user is writing a line longer than the terminal width
            self.x += 1
            
        if self.is_last_line(index) and self.file_buffer[len(self.file_buffer)-1] != '\n':
            self.file_buffer.insert(len(self.file_buffer), '\n')
            
    def get_line_length(self, direction=-1):
        counted, index = self.calculate_index()
        start_of_cur_line = (index - self.x)
        i = start_of_cur_line - 2 # places the cursor to the left of the 
        count = 0 
        
        while True:
            if self.file_buffer[i] == '\n':
                return count
            count += 1
            i += direction # traverse the list in the direction, possible directions are -1 for prev line and 1 for current line
            
    def get_next_line_length(self):
        self.x = 0
        self.y += 1 
        count = 0 
        counted, index = self.calculate_index()
        
            
        for i in range(index, len(self.file_buffer)):
            if self.file_buffer[i] == '\n':
                self.x = self.prev_x
                return count
            count += 1
        self.x = self.prev_x
        return 0
        
    def get_current_line_length(self):
        counted, index = self.calculate_index()
        start_of_line = index - self.x 
        
        i = start_of_line
        count = 0 
        
        while True:
            if self.file_buffer[i] == '\n':
                return count 
            count += 1 
            i += 1 
        
    def cursorup(self, stdscr):
        prev_line_length = self.get_line_length(-1)
        
        if not self.get_line_length(-1):
              self.y -= 1
              return 
              
        if prev_line_length < self.x:
            self.x = prev_line_length
        elif prev_line_length >= self.prev_x:
                self.x = self.prev_x 
        else:
            self.x = prev_line_length
        self.y -= 1
        return 

    def cursordown(self):
        counted, index = self.calculate_index()
        
        if self.is_last_line(index):
            self.file_buffer.insert(len(self.file_buffer)-1, '\n')
            return 
            
        next_line_length = self.get_next_line_length()
        
        
        if next_line_length < self.x:
            self.x = next_line_length          
        else:
            self.x = self.prev_x
        return
        
    def cursorright(self):
        # current_line_length = self.get_line_length(1)
        #if current_line_length == self.x:
        #        return
        self.x += 1
        self.prev_x = self.x
        return 
        
    def cursorleft(self):
        self.x -= 1
        self.prev_x = self.x
        
    def is_last_line(self, index):
        i = 0
        while True:
            try:
                if self.file_buffer[index+i] == '\n':
                    return False
            except:
                return True
            i += 1 
        
    def cursor_to_prev_line(self):
        counted, index = self.calculate_index()
        newline_on_prev_line = index - 1
        self.x = self.get_prev_line_length()
        
        del self.file_buffer[newline_on_prev_line] # delete the newline
        self.y -= 1
        
    def removelastchar(self, stdscr):
        counted, index = self.calculate_index()
        newline_on_prev_line = index - 1
        
        if self.checkbounds('x', False) and index != 0: # if the user is not deleting at the beginning of a line
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

# how to implement left/right up/down scrolling
"""
get the buffer dimensions:
    count rows in self.file_buffer by counting all the newlines
    count columns in self.file_buffer by counting the longest line 

set the window size 

"""
