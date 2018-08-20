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

const AotPlugin = require('@ngtools/webpack').AngularCompilerPlugin;
const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const helpers = require('./helpers');

module.exports = {
  entry: {
    'manage': './chrome_app/src/app/manage/main.ts',
    'onboarding': './chrome_app/src/app/onboarding/main.ts',
    'offboarding': './chrome_app/src/app/offboarding/main.ts',
    'background': './chrome_app/src/app/background/background.ts',
  },
  resolve: {extensions: ['.ts', '.js'], modules: ['node_modules']},
  module: {
    rules: [
      {
        test: /\.ts$/,
        loader: '@ngtools/webpack',
      },
      {test: /\.html$/, loader: 'html-loader'}, {
        test: /\.(png|jpe?g|gif|woff|svg|woff2|ttf|eot|ico)$/,
        loader: 'file-loader?name=assets/[name].[hash].[ext]'
      },
      {test: /\.scss$/, use: ['raw-loader', 'sass-loader']}
    ]
  },
  plugins: [
    new AotPlugin({
      tsConfigPath: './tsconfig.json',
      entryModule: helpers.root('chrome_app/src/app/manage/app#AppModule'),
    }),
    new webpack.ContextReplacementPlugin(
        /angular(\\|\/)core(\\|\/)@angular/, helpers.root('./chrome_app/src'),
        {}),
    new HtmlWebpackPlugin({
      filename: 'manage.html',
      chunks: ['manage'],
      template: 'chrome_app/src/app/manage/manage.html'
    }),
    new HtmlWebpackPlugin({
      filename: 'onboarding.html',
      chunks: ['onboarding'],
      template: 'chrome_app/src/app/onboarding/onboarding.html',
    }),
    new HtmlWebpackPlugin({
      filename: 'offboarding.html',
      chunks: ['offboarding'],
      template: 'chrome_app/src/app/offboarding/offboarding.html',
    }),
    new CopyWebpackPlugin([
      {from: './chrome_app/manifest.json', flatten: true},
      // Load necessary Roboto and Material Icon fonts
      {from: './chrome_app/src/app/assets/fonts/', to: './assets/fonts/'},
      // CSS file(s)
      {from: './chrome_app/src/app/assets/fonts.css', to: './assets/'},
      {from: './chrome_app/src/app/assets/preload.css', to: './assets/'},
      // Chrome App icons
      {from: './chrome_app/src/app/assets/icons/', to: './assets/icons/'},
      // FAQ markdown file
      {from: './chrome_app/src/app/assets/faq.md', to: './assets/faq.md'},
      // Animations
      {
        from: './chrome_app/src/app/assets/animations/',
        to: './assets/animations/'
      }
    ]),
  ]
};
