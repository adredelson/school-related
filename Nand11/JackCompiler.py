from compile_class import CompileEngine
import sys
import os.path

FILE_SUFFIX = ".vm"
ORIGINAL_SUFFIX = ".jack"

if __name__ == "__main__":
    path = sys.argv[1]
    name = os.path.basename(path)
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if os.path.isdir(path):
        for file in os.scandir(path):
            if file.name.endswith(ORIGINAL_SUFFIX):
                out = file.path[:-5] + FILE_SUFFIX
                compiler = CompileEngine(file.path, out)

    else:
        out = path[:-5] + FILE_SUFFIX
        compiler = CompileEngine(path, out)
