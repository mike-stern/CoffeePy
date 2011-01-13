import PyV8 as v8
import time
import sys
import os
import codecs

POLL_INTERVAL = 2

sys.path.append('coffee_watch')

compiled = {}


def watch_folder(folder, interval = POLL_INTERVAL):
    folder = os.path.realpath(folder)
    print "Checking %s every %d seconds" % (folder,
                                               interval
                                               )
    while True:
        try:
            _check_folder(folder)
            time.sleep(interval)
        except KeyboardInterrupt:
            # allow graceful exit (no stacktrace output)
            sys.exit(0)
        
def _check_folder(folder):

    for dirpath, dirnames, filenames in os.walk(folder):
        filepaths = (os.path.join(dirpath, filename) 
                     for filename in filenames if filename.endswith('.coffee')
                     )
        for fullpath in filepaths:
            mtime = os.stat(fullpath).st_mtime
            compiled_path = _compiled_path(fullpath)
            if (not fullpath in compiled or
                compiled[fullpath] < mtime or
                not os.path.isfile(compiled_path)):
                _compile_file(fullpath, compiled_path)
                compiled[fullpath] = mtime

def _compiled_path(fullpath):
    return fullpath[:fullpath.rfind('.')] + '.js'

def _compile_file(path, compiled_path):
    try:
        codecs.open(compiled_path, 'w', encoding='utf-8').write(_convert(codecs.open(path, 'r', encoding='utf-8').read()))
    except Exception, e:
        print "Error parsing CoffeScript in %s" % path
        

def _convert(coffee):
    ct = v8.JSContext()
    ct.enter()
    return ct.eval(open('coffee-script.js').read()).compile(coffee)

if __name__ == '__main__':
    
    if len(sys.argv) >=2:
        f = sys.argv[1] 
    else: print "Usage: python coffee_converter.py <watch_directory>"
            
    watch_folder(f)
        