# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:

# TODO: Delete this tutorial at some point.


import click


class Config(object):
    def __init__(self):
        self.verbose = False
        self.home = None


passConfig = click.make_pass_decorator(Config, ensure = True)


@click.group()
@click.option('--verbose', is_flag = True)
@click.option('--home', type = click.Path())
@passConfig
def cli(config, verbose, home):
    config.verbose = verbose
    if not home:
        config.home = home
    

@cli.command()
@click.option('--string', default='World', help='Some string, usually a name')
@click.option('--repeat', default=1, help='Number of times to show the output')
@click.argument('out', type=click.File('w'), default='-', required=False)
@passConfig
def say(config, string, repeat, out):
    """
CLI test program to learn how to use Click.  This string is part of the --help
output.
"""
    if config.verbose:
        print('We are in verbose mode')

    print('Home = %s' % config.home)

    for count in range(repeat):
        print('%d poof test => %s' % (count, string), file = out)

