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
        self.prev_x = 0 
        
        self.save = False
        self.select = select
        
        
        
        self.viewport_top = 0 
        self.viewport_bottom = self.count_chars_on_screen() 
        
        self.draw_buffer = self.file_buffer[self.viewport_top : self.viewport_bottom ] 
        
        stdscr.nodelay(True)
        
        
    def checkbounds(self, axis, is_positive_direction=True):
        if axis == 'y':
            if is_positive_direction:
                if self.y == self.rows - 1:
                    self.set_viewports()
                else:
                    return self.y < self.rows - 1
            else:
                return self.y > 0
        elif axis == 'x':
            if is_positive_direction:
                return self.x < self.cols - 1
            else:
                return self.x > 0
        return False 

    def set_viewports(self): # called when we're at the last row of the screen
        # self.viewport_bottom is always at self.x = 0 and the begining of the viewport
        # to calculate the next bottom:
        # find the length of the current line
        # add bottom to the remaining length of the current line 
        # add 2 to account for newline and bring us to the nextline

        VT_len_line = self.get_line_length(self.viewport_top, 0, 1)
        new_index = self.viewport_top + VT_len_line + 1  
        self.viewport_top = new_index

        VB_len_line = self.get_next_line_length(self.viewport_bottom)
        new_index = self.viewport_bottom + VB_len_line + 1
        self.viewport_bottom = new_index

    def calculate_index(self, rows, cols=0):
        newline = 0
        index = 0
        counted = 0
        for counted, ch in enumerate(self.file_buffer):
            if ch == '\n':
                newline += 1
                counted += 1 
            if newline == rows:
                index = counted + cols
                break
            
        return index  
        
    def count_chars_on_screen(self):
        count = 0 
        
        for counted, ch in enumerate(self.file_buffer):
            if ch == '\n':
                count += 1
            if count == self.rows:
                break
            return counted 
        
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
            self.viewport_bottom = self.count_chars_on_screen()

        if key == curses.KEY_BACKSPACE or key == 127:
            self.editbuffer(stdscr, key, False)
            self.viewport_bottom = self.count_chars_on_screen() 
        if key == curses.KEY_ENTER or key == 10:
            self.editbuffer(stdscr, '\n', True)
            self.viewport_bottom = self.count_chars_on_screen() 
            
            
        if key == 32: # space bar 
            self.editbuffer(stdscr, ' ', True)
            
        if key == 9: # tab key 
            for i in range(4):
                self.editbuffer(stdscr, ' ', True)
                
        if key == curses.KEY_F2: # ctrl+s
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
                      
        stdscr.erase()

        
        self.draw_buffer = self.file_buffer[self.viewport_top : self.viewport_bottom ] 
                                                          
        stdscr.addstr(0, 0, ''.join(self.draw_buffer))
        
        
        if self.save:
            stdscr.addstr(self.rows - 1, 10, " File {} saved ".format(self.file_obj.file_name))
            self.save = False
            time.sleep(0.5)
            
        stdscr.addstr(self.rows-1, self.cols - 30, f"{self.viewport_top}, {self.viewport_bottom}")
        stdscr.addstr(self.y, self.x, "")
        stdscr.refresh()
        return True, self.select
    
    def append(self, stdscr, key):
        index = self.calculate_index(self.y, self.x)

        try:
            self.file_buffer = self.file_buffer[:index] + [chr(key)] + self.file_buffer[index:]
        except:
            self.file_buffer = self.file_buffer[:index] + [key] + self.file_buffer[index:]

        if key == '\n': 
            self.y += 1
            self.x = 0          
        elif self.checkbounds('x', True): # if this fails, it means that the user is writing a line longer than the terminal width
            self.x += 1
        
        if self.has_newline(index) is False and self.file_buffer[len(self.file_buffer)-1] != '\n':
            self.file_buffer.insert(len(self.file_buffer), '\n')
            
    def get_line_length(self, index, xpos, direction=-1):
        start_of_cur_line = (index - xpos)
        if direction == -1:
            i = start_of_cur_line - 2 # places the cursor to the left of the 
        else: 
            i = start_of_cur_line
        count = 0 
        
        while True:
            if self.file_buffer[i] == '\n':
                return count
            count += 1
            i += direction # traverse the list in the direction, possible directions are -1 for prev line and 1 for current line
            
    def get_next_line_length(self, index):
        count = 0 
         
        for i in range(index, len(self.file_buffer)):
            if self.file_buffer[i] == '\n':
                self.x = self.prev_x
                return count
            count += 1
        self.x = self.prev_x
        return 0
        
    def get_current_line_length(self):
        index = self.calculate_index(self.y, self.x)
        start_of_line = index - self.x 
        
        i = start_of_line
        count = 0 
        
        if self.file_buffer[len(self.file_buffer) - 1] != '\n':
            self.file_buffer.append('\n')
            return 
            
        while True:
                if self.file_buffer[i] == '\n':
                    return count 
                count += 1 
                i += 1 
            
        
    def cursorup(self, stdscr):
        index = self.calculate_index(self.y, self.x)
        prev_line_length = self.get_line_length(index, self.x, -1)
        
        if not prev_line_length:
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

    def is_last_line(self, index):
        i = 0 

        while True:
            try:
                if self.file_buffer[index+i] == '\n':
                    return False
            except:
                return True 
            i += 1 
      
    def cursordown(self):
        index = self.calculate_index(self.y, self.x)

        if self.has_newline(index) is False:
            return 

        self.y += 1 
        self.x = 0 
        index = self.calculate_index(self.y, self.x)
        next_line_length = self.get_next_line_length(index)
        
        
        if next_line_length < self.x:
            self.x = next_line_length          
        else:
            self.x = self.prev_x
        return
        
    def cursorright(self):
        line_len = self.get_current_line_length()
        if self.x == line_len:
            return
        
        self.x += 1
        self.prev_x = self.x
        return 
        
    def cursorleft(self):
        self.x -= 1
        self.prev_x = self.x
        
    def is_last_line(self, index):
        index = self.calculate_index(self.y, self.x)
        line_len = self.get_line_length(len(self.file_buffer)-1, self.x, -1) 
        
        if index >= (len(self.file_buffer)-1)-line_len:
            return True
        return False
        
    def has_newline(self, index): # returns true if there is no newline on that line, false if there is one 
        i = 0
        while True:
            try:
                if self.file_buffer[index+i] == '\n':
                    return True
            except:
                return False
            i += 1 
        
    def cursor_to_prev_line(self):
        index = self.calculate_index(self.y, self.x)
        newline_on_prev_line = index - 1
        self.x = self.get_line_length(index, self.x, -1)
        
        del self.file_buffer[newline_on_prev_line] # delete the newline
        self.y -= 1
        
    def removelastchar(self, stdscr):
        index = self.calculate_index(self.y, self.x)
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
