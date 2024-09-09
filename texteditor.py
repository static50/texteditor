import sys 
from file_manager import File 
from screen import screen
import curses 
from curses import wrapper

select = 0 # which buffer is currently being written to 

def initfileobj(files: list, stdscr) -> list: 
  fileobjects = [] 
  for i, file_name in enumerate(files): 
    try:
      file = File(stdscr, file_name) 
    except FileNotFoundError:
      file.close() 
      continue 
    fileobjects.append(file) 
  return fileobjects 

def initscreenobj(fileobjects, stdscr):
  screenobjects = [] 
  for i, file_obj in enumerate(fileobjects):
    newscreen = screen(fileobjects, i, stdscr)
    screenobjects.append(newscreen)
  return screenobjects
    
def initbuffers(fileobjects, stdscr): # read the file
  for file_obj in fileobjects:
    file_obj.createnewbuffer() # create a new buffer and returns a list buffer

def programstart(screenobjects, fileobjects, stdscr):
    global select
    run = True
    
    while run:
        run, newselect = screenobjects[select].updatescreen(stdscr, fileobjects, select)
        screen.newselect = newselect  
        if not run:
          break
        if newselect != select:
          select = newselect
def setup_environment():
    try:
        # disabling flow control
        subprocess.run(['stty', '-ixon'], check=True)
        print("Flow control disabled.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run command: {e}")
      
def main(stdscr):
  filenames = sys.argv[1:] # store all file names from command line arguments with each list element being a filename
  fileobjects = initfileobj(filenames, stdscr)  # [ fileobj1, fileobj2, etc. ]
  initbuffers(fileobjects, stdscr) # creates a dictionary containing a list buffer for every text file
  screen.newselect = select
  screenobjects = initscreenobj(fileobjects, stdscr) 
  programstart(screenobjects,  fileobjects, stdscr) 

wrapper(main)




      # functions: 
      # initfileobj: creates a list of fileobjects
      # initbuffers: for each file object in the list aforementioned, initalize a buffer and read its corresponding file then copy it into the buffer
      # editfile: print that file to the screen. 
