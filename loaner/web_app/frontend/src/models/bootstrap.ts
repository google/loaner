// Copyright 2018 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/** Interface that defines the general bootstrap status of the application. */
export declare interface Status {
  enabled: boolean;
  completed: boolean;
  started: boolean;
  tasks: Task[];
}

/** Interface that defines the properties of a particular bootstrap task. */
export declare interface Task {
  name: string;
  success?: boolean;
  timestamp?: number;
  details?: string;
}

/** Interface that defines which (if any) bootstrap tasks should be (re)run. */
export declare interface TaskRequest {
  requested_tasks: string[];
}
