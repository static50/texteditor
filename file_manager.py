import curses 

class File:
  buffer = [] 
  file_name = None
  file = None 
  
  def __init__(self, stdscr, file_name):
    self.file_name = file_name # set the file name when the class instance is created
    try: 
      self.file = open(file_name, 'r+') # FILE OBJECT open for reading and writing 
    except FileNotFoundError:
      stdscr.erase()
      stdscr.addstr("File not found. Would you like to create a new file? y/n") 
      stdscr.refresh()
      answer = stdscr.getkey().upper()
      if answer == 'Y':
        self.file = open(file_name, 'w+') 
      if answer == 'N':
        raise FileNotFoundError(f"file {file_name} not found and not created.") 
      # make the file if its not found
    except Exception as e:
      (f"An error occurred: {e}") 
      self.file.close()
    self.buffer = []
    
  def createnewbuffer(self):
    text = self.file.read() # a string containing the text from the file
    self.buffer = list(text)   
    return 

  def get_buffer_dimensions():
    if not self.buffer:
        return (0, 0)
    lines = ''.join(self.buffer).split('\n')
    rows = len(lines)
    cols = max(len(line) for line in lines) if lines else 0
    return (rows, cols)
  
  def savefile(self, file, newbuffer):
    self.file.seek(0) # move file pointer to the beginning
    self.file.truncate() # from the file pointer onwards, delete to the end until a EOF is found 
    self.file.write(''.join(newbuffer)) # writes to a buffer ( decided by the system library ) 
    self.file.flush() # forces this buffer to be written to disk   
    return  


