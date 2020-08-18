import time
import argparse
from amazon_scraper.scraper import Scraper


def main():
    """Takes command line argument
    """
    parser = argparse.ArgumentParser(
        description='Extracts links contained in a url'
    )
    parser.add_argument(
        '-w',
        '--word',
        nargs='*',
        default='smart phone',
        help='Enter the word you want to search'
    )

    arg = parser.parse_args()
    arg.word = ' '.join(arg.word)
    amazon = Scraper()
    amazon.search(arg.word)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    stop = time.perf_counter()
    print(stop - start)
