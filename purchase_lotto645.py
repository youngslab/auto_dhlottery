#!python3

# fmt: off
import sys

from lotto645 import main as lotto_main
# fmt: on

if __name__ == "__main__":
    sys.exit(lotto_main(["--purchase", *sys.argv[1:]]))
