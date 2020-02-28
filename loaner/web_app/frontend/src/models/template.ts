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

/** Interface with fields that come from our Template API. */
export declare interface TemplateApiParams {
  name?: string;
  title?: string;
  body?: string;
}

/** Interface with fields to create a new template. */
export declare interface CreateTemplateRequest {
  template: TemplateApiParams;
}

/** Interface with fields to remove a new template. */
export declare interface RemoveTemplateRequest {
  name: string;
}

/** Interface with fields returned from a list template request. */
export declare interface ListTemplateResponseApiParams {
  templates: TemplateApiParams[];
}

/**
 * Interface with template objects created from the
 * ListTemplateResponseApiParams returned from the backend.
 */
export declare interface ListTemplateResponse {
  templates: Template[];
}

/** A Template model with all properties and methods. */
export class Template {
  /** Name of the template. */
  name = '';
  /** title or suject line of the template. */
  title = '';
  /** body for the template. */
  body = '';

  constructor(template: TemplateApiParams = {}) {
    this.name = template.name || this.name;
    this.title = template.title || this.title;
    this.body = template.body || this.body;
  }

  /** Translates the Template model object to the API message. */
  toApiMessage(): TemplateApiParams {
    return {
      name: this.name,
      title: this.title,
      body: this.body,
    };
  }
}
