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

const path = require('path');
const webpack = require('webpack');
const HtmlWebpack = require('html-webpack-plugin');
const {CommonsChunkPlugin} = require('webpack').optimize;
const CopyWebpackPlugin = require('copy-webpack-plugin');

const rootDir = path.join(process.cwd());

module.exports = {
  output: {
    path: path.resolve(rootDir, 'web_app', 'frontend', 'dist'),
    filename: 'application.js'
  },
  resolve: {extensions: ['.ts', '.js'], modules: ['node_modules']},
  module: {
    rules: [
      {test: /\.html$/, loader: 'html-loader'},
      {test: /\.scss$/, use: ['raw-loader', 'sass-loader']}
    ]
  },
  plugins: [
    new HtmlWebpack({
      filename: 'index.html',
      inject: 'body',
      template:
          path.resolve(rootDir, 'web_app', 'frontend', 'src', 'index.html')
    }),
    // Workaround for angular/angular#11580
    new webpack.ContextReplacementPlugin(
        /angular(\\|\/)core(\\|\/)@angular/,
        path.resolve(
            rootDir,
            'web_app',
            'frontend',
            'src'
            ),
        {}),
    new CopyWebpackPlugin([{
      from: 'web_app/frontend/src/assets',
      to: 'assets',
    }])
  ],
  devServer: {
    'historyApiFallback': true,
    'disableHostCheck': true,
  }
};
