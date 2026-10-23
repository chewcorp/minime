import argparse

import calc


def main(argv=None):
    parser = argparse.ArgumentParser(prog="calc")
    sub = parser.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("a", type=float)
    add.add_argument("b", type=float)
    args = parser.parse_args(argv)
    if args.cmd == "add":
        print(calc.add(args.a, args.b))


if __name__ == "__main__":
    main()
