import click
from checker import run


@click.command()

@click.option(
    "-c", "--count", default=5, help="How many relays are needed. Def: 5"
)
@click.option(
    "-o", "--output", default=None, help="File to save. Def: None"
)
@click.option(
    "-p", "--proxy", default=None, help="Proxy to get relays(http). Def: None"
)
@click.option(
    "-T", "--threads", default=100, help="How many threads are needed. Def: 100"
)
@click.option(
    "-t", "--time", default=1, help="Timeout for checking the relay(sec). Def: 1"
)
def start(count, output, proxy, threads, time):
    """Fast checker relay for tor with multiple threads."""
    run(count, output, proxy, threads, time)


if __name__ == "__main__":
    start()
