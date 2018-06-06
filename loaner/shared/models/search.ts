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

/**
 * Translate SortingDirection enum to backend SortDirection message.
 * Backend message: web_app/backend/api/messages/shared_messages.py
 * @param sorting Sorting direction from the frontend
 */
export function translateSortDirectionToApi(sorting: SortDirection) {
  return sorting === 'asc' ? 0 : 1;
}

export type SortDirection = 'asc'|'desc';

export declare interface SearchExpression {
  expression: string;
  direction?: 0|1;
}

export declare interface SearchQuery {
  query_string?: string;
  expressions?: SearchExpression;
}
