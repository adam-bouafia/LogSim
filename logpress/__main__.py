"""
Entry point for python -m logpress
"""

import click
from logpress import __version__
from logpress.cli import compress, query

@click.group()
@click.version_option(version=__version__)
def cli():
    """logpress - Semantic Log Compression System"""
    pass

cli.add_command(compress)
cli.add_command(query)

if __name__ == '__main__':
    cli()
