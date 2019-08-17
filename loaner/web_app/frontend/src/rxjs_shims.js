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
 * @fileoverview Provides named UMD shims for `rxjs/operators` and `rxjs/testing`.
 * This file should be included in the "scripts" of a "ts_devserver"
 * rule and the "deps" of a "ts_web_test_suite" rule.
 */
// rxjs/operators
(function(factory) {
    if (typeof module === 'object' && typeof module.exports === 'object') {
      var v = factory(require, exports);
      if (v !== undefined) module.exports = v;
    } else if (typeof define === 'function' && define.amd) {
      define('rxjs/operators', ['exports', 'rxjs'], factory);
    }
  })(function(exports, rxjs) {
    'use strict';
    Object.keys(rxjs.operators).forEach(function(key) { exports[key] = rxjs.operators[key]; });
    Object.defineProperty(exports, '__esModule', {value: true});
  });

  // rxjs/testing
  (function(factory) {
    if (typeof module === 'object' && typeof module.exports === 'object') {
      var v = factory(require, exports);
      if (v !== undefined) module.exports = v;
    } else if (typeof define === 'function' && define.amd) {
      define('rxjs/testing', ['exports', 'rxjs'], factory);
    }
  })(function(exports, rxjs) {
    'use strict';
    Object.keys(rxjs.testing).forEach(function(key) { exports[key] = rxjs.testing[key]; });
    Object.defineProperty(exports, '__esModule', {value: true});
  });
