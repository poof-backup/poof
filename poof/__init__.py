# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


import argparse


# *** constants ***

VALID_COMMANDS = ( 'upload', 'download', 'verify', 'test' )


# *** functions ***

def _parseCLI():
    config = dict()
    parser = argparse.ArgumentParser()

    parser.add_argument('command', type=str, help = '|'.join(VALID_COMMANDS))

    args = parser.parse_args()
    
    config['command'] = args.command

    if config['command'] not in VALID_COMMANDS:
        # TODO: Define a cleaner exit here.
        raise NotImplementedError

    return config


def main():
    config = _parseCLI()

    if config['command'] == 'test':
        return True

    # Implementation goes here.


# *** main ***

if '__main__' == __name__:
    main()

