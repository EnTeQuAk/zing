#-*- coding: utf-8 -*-
"""
    zing.cli
    ~~~~~~~~

    Command line interface.
"""
import argparse


def launch_worker(args):
    from zing.worker import Worker
    import zing.consumers

    try:
        worker = Worker(credentials={
            'aws_access_key_id': args.aws_key,
            'aws_secret_access_key': args.aws_secret
        })
        worker.add_consumer(
            queue_name='zing.event',
            consumer=zing.consumers.consume_events,
        )
        worker.run()
    except KeyboardInterrupt:
        print 'Shutting down'
        worker.stop()


def get_parser():
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(description='Zing')

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode.'
    )
    parser.add_argument(
        "--aws-key",
        default=None,
        help="AWS API key to use. Falls back to boto's config search."
    )
    parser.add_argument(
        "--aws-secret",
        default=None,
        help="AWS API key secret to use. Falls back to boto's config search."
    )

    subparsers = parser.add_subparsers()

    parser_worker = subparsers.add_parser('worker')
    parser_worker.set_defaults(func=launch_worker)

    return parser


def main():
    parser = get_parser()

    args = parser.parse_args()

    # TODO: set debug mode

    # Run the CLI command
    args.func(args)


if __name__ == '__main__':
    main()
