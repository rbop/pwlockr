import argparse

from keybox.memlock import memlock
from keybox import pwgen, shell, ui


def run_print(keybox_file, filter_expr):
    base_ui = ui.BaseUI(keybox_file)
    if not base_ui.open(readonly=True):
        return
    print("Searching for %r..." % filter_expr)
    base_ui.cmd_select(filter_expr)
    if not base_ui.selected:
        return
    base_ui.cmd_print()


def run_shell(keybox_file, readonly, timeout, no_memlock):
    if not no_memlock:
        memlock()
    shell.SHELL_TIMEOUT_SECS = timeout
    shell_ui = shell.ShellUI(keybox_file)
    shell_ui.start(readonly)


def run_pwgen(length, words, upper, digits, special):
    for _ in range(10):
        print(pwgen.generate_password(length),
              pwgen.generate_passphrase(words, length, upper, digits, special),
              sep='   ')


def run_export(keybox_file, output_file, file_format):
    base_ui = ui.BaseUI(keybox_file)
    if not base_ui.open(readonly=True):
        return
    base_ui.cmd_export(output_file, file_format)


def run_import(keybox_file, import_file, file_format):
    base_ui = ui.BaseUI(keybox_file)
    if not base_ui.open():
        return
    base_ui.cmd_import(import_file, file_format)
    base_ui.close()


def parse_args():
    """Process command line args."""
    ap = argparse.ArgumentParser(prog="keybox",
                                 description="Keybox manager",
                                 formatter_class=argparse.RawTextHelpFormatter)

    # Sub-commands
    sp = ap.add_subparsers()
    ap_shell = sp.add_parser("shell", aliases=['sh'],
                             help="start shell (default)")
    ap_shell.set_defaults(func=run_shell)
    ap_pwgen = sp.add_parser("pwgen", help="generate random password")
    ap_pwgen.set_defaults(func=run_pwgen)
    ap_export = sp.add_parser("export", help="export content of keybox file")
    ap_export.set_defaults(func=run_export)
    ap_import = sp.add_parser("import", help="import records from a file")
    ap_import.set_defaults(func=run_import, file_format='keybox')
    ap_print = sp.add_parser("print", aliases=['p'],
                             help="print key specified by pattern")
    ap_print.set_defaults(func=run_print)

    for subparser in (ap_shell, ap_import, ap_export, ap_print):
        subparser.add_argument('-f', dest='keybox_file',
                               default=shell.ShellUI.get_default_filename(),
                               help="keybox file (default: %(default)s)")

    ap_shell.add_argument('-r', dest="readonly", action='store_true',
                          help="open keybox in read-only mode")
    ap_shell.add_argument('--no-memlock', action='store_true',
                          help="Do not try to lock memory")
    ap_shell.add_argument('--timeout', type=int, default=shell.SHELL_TIMEOUT_SECS,
                          help="Save and quit when timeout expires "
                               "(default: %(default)s)")

    ap_import.add_argument('import_file', type=str,
                           help="the file to be imported ('-' for stdin)")
    ap_export.add_argument('-o', dest='output_file', type=str, default='-',
                           help="use this file instead of stdout")
    for subparser in (ap_import, ap_export):
        format_grp = subparser.add_mutually_exclusive_group(required=(subparser == ap_export))
        format_grp.add_argument('--plain', dest='file_format', action='store_const', const='plain',
                                help="select plain-text format")
        format_grp.add_argument('--json', dest='file_format', action='store_const', const='json',
                                help="select JSON format")

    ap_pwgen.add_argument('-l', dest='length', type=int, default=pwgen.MIN_LENGTH,
                          help="pwgen: minimal length of password "
                               "(default: %(default)s)")
    ap_pwgen.add_argument('-w', dest='words', type=int, default=pwgen.NUM_WORDS,
                          help="pwgen: number of words to concatenate "
                               "(default: %(default)s)")
    ap_pwgen.add_argument('-u', dest='upper', type=int, default=pwgen.NUM_UPPER,
                          help="pwgen: number of letters to make uppercase "
                               "(default: %(default)s)")
    ap_pwgen.add_argument('-d', dest='digits', type=int, default=pwgen.NUM_DIGITS,
                          help="pwgen: number of digits to add "
                               "(default: %(default)s)")
    ap_pwgen.add_argument('-s', dest='special', type=int, default=pwgen.NUM_SPECIAL,
                          help="pwgen: number of special symbols to add "
                               "(default: %(default)s)")

    ap_print.add_argument('filter_expr',
                          help="Expression for selecting record to be printed. "
                               "Format is [<column>:]<text>. "
                               "Default <column> is 'site,url'. ")

    args = ap.parse_args()

    if 'func' not in args:
        ap_shell.parse_args(namespace=args)

    return args


def main():
    args = parse_args()
    run_func = args.func
    delattr(args, 'func')
    run_func(**vars(args))
