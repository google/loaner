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

import {Component, OnDestroy, OnInit} from '@angular/core';
import {AbstractControl, FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Subject} from 'rxjs';
import {takeUntil} from 'rxjs/operators';
import {Template} from '../../models/template';
import {Dialog} from '../../services/dialog';
import {TemplateService} from '../../services/template';

const CONFIRM_TITLE = 'Are you sure?';
const ARE_YOU_SURE = 'Are you sure you want to';

/**
 * Component that renders the email template editor.
 */
@Component({
  selector: 'loaner-email-template',
  styleUrls: ['email_template.scss'],
  templateUrl: 'email_template.ng.html',
})
export class EmailTemplate implements OnInit, OnDestroy {
  destroyed = new Subject<boolean>();
  showNewView = false;
  templates: Template[] = [];
  templatesForm: FormGroup = this.fb.group({
    selected: this.fb.group({template: new Template()}),
    template: this.fb.group({
      name: [null, Validators.required],
      title: '',
      body: '',
    })
  });

  constructor(
      private readonly templateService: TemplateService,
      private readonly fb: FormBuilder,
      private readonly dialog: Dialog,
  ) {}

  ngOnInit() {
    this.selectedTemplate.valueChanges.pipe(takeUntil(this.destroyed))
        .subscribe(value => {
          if (value) {
            this.template.setValue({...value});
          }
        });
    this.getTemplateList();
  }

  ngOnDestroy() {
    this.destroyed.next(true);
    this.destroyed.unsubscribe();
  }

  get selectedTemplate(): AbstractControl {
    return this.templatesForm.get(['selected', 'template'])!;
  }

  get template(): AbstractControl {
    return this.templatesForm.get(['template'])!;
  }

  /** Changes to Add New View on button click. */
  addNewView() {
    this.showNewView = true;
    this.templatesForm.reset();
  }

  /** Adds a new template on email template on add button click. */
  addTemplate() {
    this.templateService.create(new Template(this.template.value))
        .subscribe(() => {
          this.goBackToEditView(true);
        });
  }

  /** Retrieves Template List and binds it to model. */
  getTemplateList(selectIndex: number = 0) {
    const selectedIndex = (selectIndex && selectIndex > -1) ? selectIndex : 0;
    this.templateService.list().subscribe(response => {
      this.templates = response.templates;
      this.selectedTemplate.setValue(
          this.templates[selectedIndex], {onlySelf: true});
    });
  }

  /**
   * Switches showNewView to false and resets form and calls getTemplateList.
   */
  goBack() {
    this.showNewView = false;
    this.templatesForm.reset();
    this.getTemplateList();
  }

  /** Goes back to edit template view. */
  goBackToEditView(noConfirm: boolean) {
    const action = 'You are attempting to navigate back.';
    const msg = `${action}  ${ARE_YOU_SURE} stop creating this template?`;
    if (noConfirm) {
      this.goBack();
    } else {
      this.dialog.confirm(CONFIRM_TITLE, msg).subscribe(result => {
        if (result) this.goBack();
      });
    }
  }

  /** Removes template by name on button click. */
  removeTemplate() {
    const action = 'You are removing a template.';
    const msg = `${action}  ${ARE_YOU_SURE} remove this template?`;
    this.dialog.confirm(CONFIRM_TITLE, msg).subscribe(result => {
      if (result) {
        this.templateService.remove(new Template(this.template.value))
            .subscribe(() => {
              this.goBack();
            });
      }
    });
  }

  /** Saves updated template on email template change button click. */
  saveTemplate() {
    const updateTemplate = new Template(this.template.value);
    this.templateService.update(updateTemplate).subscribe(() => {
      const selectIndex =
          this.templates.findIndex(item => item.name === updateTemplate.name);
      this.getTemplateList(selectIndex);
    });
  }
}
