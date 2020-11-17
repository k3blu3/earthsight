'''
run.py

Entry-point for command line execution
'''


import os


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    notebook_file = os.path.join(dir_path, 'earthsight.ipynb')
    cmd = 'voila --enable_nbextensions=True {}'.format(notebook_file)
    os.system(cmd)


if __name__ == "__main__":
    main()
