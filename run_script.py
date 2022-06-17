import sys

from scripts import load_knowledge

from scripts import load_knowledge_from_excel


def no_script():
    print('Script not Found')


scripts = {
    'load': load_knowledge.load,
    'xls': load_knowledge_from_excel.load
}


def main():
    args = sys.argv
    scripts.get(args[1], no_script)()


if __name__ == "__main__":
    main()
