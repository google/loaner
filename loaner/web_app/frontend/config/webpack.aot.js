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

const AngularCompilerPlugin = require('@ngtools/webpack').AngularCompilerPlugin;
const path = require('path');
var webpack = require('webpack');
var UglifyJsPlugin = require('uglifyjs-webpack-plugin');
var webpackMerge = require('webpack-merge');
var commonConfig = require('./webpack.common.js');

const rootDir = path.join(__dirname);

module.exports = webpackMerge(commonConfig, {
  entry: {main: './web_app/frontend/src/main.aot.ts'},
  module: {
    rules: [
      {
        test: /(?:\.ngfactory\.js|\.ngstyle\.js|\.ts)$/,
        loader: '@ngtools/webpack',
      },
    ]
  },
  plugins: [
    new AngularCompilerPlugin({
      tsConfigPath: './tsconfig.json',
      entryModule: path.resolve(rootDir, 'web_app/frontend/src/app#AppModule'),
      sourceMap: true,
    }),
    new webpack.NoEmitOnErrorsPlugin(), new UglifyJsPlugin({
      uglifyOptions: {
        output: {
          comments: false,
        },
      }
    }),
    new webpack.LoaderOptionsPlugin({
      htmlLoader: {
        minimize: false  // workaround for ng2
      }
    })
  ]
});
