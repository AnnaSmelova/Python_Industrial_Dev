import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from task_Smelova_Anna_graphite_cli import setup_parser, configure_response, \
    DEFAULT_HOST, DEFAULT_PORT, DEFAULT_DATASET_PATH


def test_can_setup_parser():
    parser = ArgumentParser(
        prog="graphite_cli",
        description="tool to convert log file",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)


def test_parser_response(capsys):
    configure_response(DEFAULT_DATASET_PATH, DEFAULT_HOST, DEFAULT_PORT)
    captured = capsys.readouterr()
    assert DEFAULT_HOST, DEFAULT_PORT in captured.out


def test_entrypoint():
    exit_status = os.system('python3 task_Smelova_Anna_graphite_cli.py -h')
    assert exit_status == 0
