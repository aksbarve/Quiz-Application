# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for flags for `gcloud tasks` commands."""

import sys

from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.tasks import constants


def AddQueueResourceArg(parser, verb):
  base.Argument('queue', help='The queue {}.\n\n'.format(verb)).AddToParser(
      parser)


def AddQueueResourceFlag(parser, required=True, plural_tasks=False):
  description = ('The queue the tasks belong to.' if plural_tasks else
                 'The queue the task belongs to.')
  argument = base.Argument('--queue', help=description, required=required)
  argument.AddToParser(parser)


def AddTaskResourceArgs(parser, verb):
  base.Argument('task', help='The task {}.\n\n'.format(verb)).AddToParser(
      parser)
  AddQueueResourceFlag(parser, required=False)


def AddIdArg(parser, noun, verb, metavar=None):
  metavar = metavar or '{}_ID'.format(noun.replace(' ', '_').upper())
  argument = base.Argument('id', metavar=metavar,
                           help='ID of the {} {}.\n\n'.format(noun, verb))
  argument.AddToParser(parser)


def AddCreatePullQueueFlags(parser):
  for flag in _PullQueueFlags():
    flag.AddToParser(parser)


def AddCreateAppEngineQueueFlags(parser):
  for flag in _AppEngineQueueFlags():
    flag.AddToParser(parser)


def AddUpdatePullQueueFlags(parser):
  for flag in _PullQueueFlags():
    _AddFlagAndItsClearEquivalent(flag, parser)


def AddUpdateAppEngineQueueFlags(parser):
  for flag in _AppEngineQueueFlags():
    _AddFlagAndItsClearEquivalent(flag, parser)


def _AddFlagAndItsClearEquivalent(flag, parser):
  update_group = base.ArgumentGroup(mutex=True)
  update_group.AddArgument(flag)
  update_group.AddArgument(_EquivalentClearFlag(flag))
  update_group.AddToParser(parser)


def _EquivalentClearFlag(flag):
  name = flag.name.replace('--', '--clear-')
  clear_flag = base.Argument(
      name, action='store_true', help="""\
      Clear the field corresponding to `{}`.""".format(flag.name))
  return clear_flag


def AddPolicyFileFlag(parser):
  base.Argument('policy_file', help="""\
      JSON or YAML file containing the IAM policy.""").AddToParser(parser)


def AddTaskLeaseScheduleTimeFlag(parser, verb):
  base.Argument(
      '--schedule-time', required=True,
      help="""\
      The task's current schedule time. This restriction is to check that the
      caller is {} the correct task.
      """.format(verb)).AddToParser(parser)


def AddTaskLeaseDurationFlag(parser, helptext=None):
  if helptext is None:
    helptext = ('The number of seconds for the desired new lease duration, '
                'starting from now. The maximum lease duration is 1 week.')
  base.Argument('--lease-duration', required=True, type=int,
                help=helptext).AddToParser(parser)


def AddMaxTasksToPullFlag(parser):
  # Default help for base.LIMIT_FLAG is inaccurate and confusing in this case
  base.Argument(
      '--limit', type=int, default=1000, category=base.LIST_COMMAND_FLAGS,
      help="""\
      The maximum number of tasks to lease. The maximum that can be requested is
      1000.
      """).AddToParser(parser)


def AddFilterPulledTasksFlag(parser):
  tag_filter_group = parser.add_mutually_exclusive_group()
  tag_filter_group.add_argument('--tag', help="""\
      A tag to filter each task to be pulled. If a task has the tag and the
      task is available to be pulled, then it is listed and leased.
      """)
  tag_filter_group.add_argument('--oldest-tag', action='store_true', help="""\
      Only pull tasks which have the same tag as the task with the oldest
      schedule time.
      """)


def AddCreatePullTaskFlags(parser):
  """Add flags needed for creating a pull task to the parser."""
  AddQueueResourceFlag(parser, required=False)
  for flag in _PullTaskFlags():
    flag.AddToParser(parser)
  _AddPayloadFlags(parser)


def AddCreateAppEngineTaskFlags(parser):
  """Add flags needed for creating a App Engine task to the parser."""
  AddQueueResourceFlag(parser, required=False)
  for flag in _AppEngineTaskFlags():
    flag.AddToParser(parser)
  _AddPayloadFlags(parser)


def _PullQueueFlags():
  return [
      base.Argument(
          '--max-attempts',
          type=arg_parsers.BoundedInt(1, sys.maxint, unlimited=True),
          help="""\
          The maximum number of attempts per task in the queue.
          """),
      base.Argument(
          '--max-retry-duration',
          help="""\
          The time limit for retrying a failed task, measured from when the task
          was first run. Once the `--max-retry-duration` time has passed and the
          task has been attempted --max-attempts times, no further attempts will
          be made and the task will be deleted.

          Must be a string that ends in 's', such as "5s".
          """),
  ]


def _AppEngineQueueFlags():
  return _PullQueueFlags() + [
      base.Argument(
          '--max-tasks-dispatched-per-second',
          type=float,
          help="""\
          The maximum rate at which tasks are dispatched from this queue. This
          also determines "max burst size" for App Engine queues: if
          `--max-tasks-dispatched-per-second` is 1, then max burst size is 10;
          otherwise it is `max-tasks-dispatched-per-second` / 5.
          """),
      base.Argument(
          '--max-concurrent-tasks',
          type=int,
          help="""\
          The maximum number of concurrent tasks that Cloud Tasks allows to
          be dispatched for this queue. After this threshold has been reached,
          Cloud Tasks stops dispatching tasks until the number of outstanding
          requests decreases.
          """),
      base.Argument(
          '--max-doublings',
          type=int,
          help="""\
          The maximum number of times that the interval between failed task
          retries will be doubled before the increase becomes constant. The
          constant is: min-backoff * 2 ** (max-doublings - 1).
          """),
      base.Argument(
          '--min-backoff',
          help="""\
          The minimum amount of time to wait before retrying a task after it
          fails. Must be a string that ends in 's', such as "5s".
          """),
      base.Argument(
          '--max-backoff',
          help="""\
          The maximum amount of time to wait before retrying a task after it
          fails. Must be a string that ends in 's', such as "5s".
          """),
      base.Argument(
          '--routing-override',
          type=arg_parsers.ArgDict(key_type=_GetAppEngineRoutingKeysValidator(),
                                   min_length=1, max_length=3,
                                   operators={':': None}),
          metavar='KEY:VALUE',
          help="""\
          If provided, the specified route is used for all tasks in the queue,
          no matter what is set is at the task-level.

          KEY must be at least one of: [{}]. Any missing keys will use the
          default.
          """.format(', '.join(constants.APP_ENGINE_ROUTING_KEYS))),
  ]


def _PullTaskFlags():
  return _CommonTaskFlags() + [
      base.Argument('--tag', help="""\
          An optional label used to group similar tasks.
          """),
  ]


def _AppEngineTaskFlags():
  return _CommonTaskFlags() + [
      base.Argument('--method', help="""\
          The HTTP method to use for the request. If not specified, "POST" will
          be used.
          """),
      base.Argument('--url', help="""\
          The relative URL of the request. Must begin with "/" and must be a
          valid HTTP relative URL. It can contain a path and query string
          arguments. If not specified, then the root path "/" will be used.
          """),
      base.Argument('--header', metavar='HEADER_FIELD: HEADER_VALUE',
                    action='append', type=_GetHeaderArgValidator(),
                    help="""\
          An HTTP request header. Header values can contain commas. This flag
          can be repeated. Repeated header fields will have their values
          overridden.
          """),
      base.Argument(
          '--routing',
          type=arg_parsers.ArgDict(key_type=_GetAppEngineRoutingKeysValidator(),
                                   min_length=1, max_length=3,
                                   operators={':': None}),
          metavar='KEY:VALUE',
          help="""\
          The route to be used for this task. KEY must be at least one of:
          [{}]. Any missing keys will use the default.

          Routing can be overridden by the queue-level `--routing-override`
          flag.
          """.format(', '.join(constants.APP_ENGINE_ROUTING_KEYS))),
  ]


def _CommonTaskFlags():
  return [
      base.Argument(
          '--id', required=False, metavar='TASK_ID',
          help="""\
          The ID of the task to create.

          If not specified then the system will generate a random unique task
          ID. Explicitly specifying a task ID enables task de-duplication. If a
          task's ID is identical to that of an existing task or a task that was
          deleted or completed recently then the call will fail.

          Because there is an extra lookup cost to identify duplicate task
          names, tasks created with IDs have significantly increased latency.
          Using hashed strings for the task ID or for the prefix of the task ID
          is recommended.
          """),
      base.Argument('--schedule-time', help="""\
          The time when the task is scheduled to be first attempted. Defaults to
          "now" if not specified.
          """)
  ]


def _AddPayloadFlags(parser):
  payload_group = parser.add_mutually_exclusive_group()
  payload_group.add_argument('--payload-content', help="""\
          Data payload to be consumed by the task worker to process the task.
          """)
  payload_group.add_argument('--payload-file', help="""\
          File containing data payload to be consumed by the task worker to
          execute the task. The payload will be sent as the HTTP message body. A
          message body, and thus a payload, is allowed only if the HTTP method
          is "POST" or "PUT".
          """)


def _GetAppEngineRoutingKeysValidator():
  return arg_parsers.CustomFunctionValidator(
      lambda k: k in constants.APP_ENGINE_ROUTING_KEYS,
      'Only the following keys are valid for routing: [{}].'.format(
          ', '.join(constants.APP_ENGINE_ROUTING_KEYS)))


def _GetHeaderArgValidator():
  return arg_parsers.RegexpValidator(
      r'^(\S+):(.+)$', 'Must be of the form: "HEADER_FIELD: HEADER_VALUE".')
