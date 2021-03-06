# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Shared constants used by container commands."""

EXPIRE_WARNING_DAYS = 14

EXPIRE_WARNING = """
! One or more clusters are approaching expiration and will be deleted.
"""

KUBERNETES_ALPHA_PROMPT = (
    "This will create a cluster with all Kubernetes Alpha features enabled.\n"
    "- This cluster will not be covered by the Kubernetes Engine SLA and should"
    " not be used for production workloads.\n"
    "- You will not be able to upgrade the master or nodes.\n"
    "- The cluster will be deleted after 30 days.\n"
)

KUBERNETES_REGIONAL_CHARGES_PROMPT = (
    "This will create a regional cluster.\n"
    "While this feature is available at no charge in Alpha, "
    "in the future you may be charged for it.\n"
)

KUBERNETES_API_MISMATCH_PROMPT_TEMPLATE = (
    "Warning: you invoked `gcloud {track}`, but with current configuration "
    "Kubernetes Engine v1 API will be used instead of {api} API.\n"
    "If you intended to use {api} API instead, please set "
    "container/use_v1_api_client property to false.")

USERNAME_PASSWORD_ERROR_MSG = (
    "Cannot specify --password with empty --username or --no-enable-basic-auth."
)
