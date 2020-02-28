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

import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatDialogModule} from '@angular/material/dialog';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {Template} from '../../models/template';
import {DialogsModule} from '../../services/dialog';
import {Dialog} from '../../services/dialog';
import {TemplateService} from '../../services/template';
import {TemplateServiceMock} from '../../testing/mocks';

import {EmailTemplate, EmailTemplateModule} from './index';

describe('EmailTemplateComponent', () => {
  let fixture: ComponentFixture<EmailTemplate>;
  let emailTemplate: EmailTemplate;
  let dialogService: Dialog;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            BrowserAnimationsModule,
            DialogsModule,
            EmailTemplateModule,
            FormsModule,
            MatDialogModule,
            ReactiveFormsModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: TemplateService, useClass: TemplateServiceMock}, Dialog
          ]
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(EmailTemplate);
    dialogService = TestBed.get(Dialog);
    emailTemplate = fixture.debugElement.componentInstance;
    fixture.detectChanges();
  }));

  afterEach(() => {
    emailTemplate.showNewView = false;
  });

  // Create reusable function for a dry spec.
  function updateForm(name: string, body: string, title: string) {
    const updateFormTemplate = new Template({name, body, title});
    emailTemplate.templatesForm.controls['template'].setValue(
        updateFormTemplate);
  }

  // Create reusable function for a dry spec.
  function updateTemplateSelected(name: string, body: string, title: string) {
    const updateFormTemplate = new Template({name, body, title});
    emailTemplate.selectedTemplate.setValue(updateFormTemplate);
  }

  it('should render', () => {
    expect(emailTemplate).toBeTruthy();
  });

  it('onInit calls getTemplateList and sets selectedTemplate', () => {
    spyOn(emailTemplate, 'getTemplateList').and.callThrough();
    emailTemplate.ngOnInit();
    fixture.detectChanges();
    expect(emailTemplate.getTemplateList).toHaveBeenCalledTimes(1);
    emailTemplate.selectedTemplate.valueChanges.subscribe(() => {
      expect(emailTemplate.template.value).toEqual({
        name: 'test_email_template_1',
        title: 'test_title',
        body: 'hello world'
      });
    });
  });

  describe('addNewView', () => {
    it('sets showNewView prop and resets form', () => {
      spyOn(emailTemplate.templatesForm, 'reset').and.callThrough();
      emailTemplate.addNewView();
      fixture.detectChanges();
      expect(emailTemplate.showNewView).toBe(true);
      expect(emailTemplate.templatesForm.reset).toHaveBeenCalledTimes(1);
    });

    it('clicking button opens add new template view', () => {
      const compiled = fixture.debugElement.nativeElement;
      const addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      const addNewButton =
          compiled.querySelector('button[name="add-new-template"]');
      spyOn(emailTemplate, 'addNewView').and.callThrough();
      expect(addNewViewButton).toBeDefined();
      addNewViewButton.click();
      expect(emailTemplate.addNewView).toHaveBeenCalledTimes(1);
      fixture.detectChanges();
      expect(emailTemplate.showNewView).toEqual(true);
      expect(addNewButton).toBeDefined();
    });
  });

  describe('addTemplate', () => {
    it('calls TemplateService.create and calls goBackToEditView', () => {
      const templateService = TestBed.get(TemplateService);
      updateForm('testName', 'testBody', 'testTitle');
      spyOn(templateService, 'create').and.callThrough();
      spyOn(emailTemplate, 'goBackToEditView').withArgs(true).and.callThrough();
      emailTemplate.addTemplate();
      fixture.detectChanges();
      expect(templateService.create).toHaveBeenCalledTimes(1);
      templateService.create(new Template(emailTemplate.template.value))
          .subscribe(() => {
            expect(emailTemplate.goBackToEditView).toHaveBeenCalledWith(true);
          });
    });

    it('clicking button creates Template and goes back to edit view', () => {
      const templateNameInput =
          emailTemplate.templatesForm.get(['template', 'name']);
      const compiled = fixture.debugElement.nativeElement;
      let addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      const templateService = TestBed.get(TemplateService);
      spyOn(templateService, 'create').and.callThrough();
      spyOn(emailTemplate, 'addTemplate').and.callThrough();
      spyOn(emailTemplate, 'goBackToEditView').and.callThrough();
      spyOn(emailTemplate, 'goBack').and.callThrough();
      addNewViewButton.click();
      fixture.detectChanges();
      let addNewTemplateButton =
          compiled.querySelector('button[name="add-new-template"]');
      addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      expect(addNewTemplateButton).toBeTruthy();
      expect(addNewViewButton).toBeFalsy();
      templateNameInput!.setValue('test');
      expect(emailTemplate.templatesForm.valid).toBeTruthy();
      addNewTemplateButton.click();
      fixture.detectChanges();
      templateService.create(new Template(emailTemplate.template.value))
          .subscribe(() => {
            expect(emailTemplate.addTemplate).toHaveBeenCalledTimes(1);
            expect(templateService.create).toHaveBeenCalledTimes(1);
            expect(emailTemplate.goBackToEditView).toHaveBeenCalledTimes(1);
            expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
            const addViewNewButtonShow =
                compiled.querySelector('button[name="show-new-template-view"]');
            addNewTemplateButton =
                compiled.querySelector('button[name="back-to-edit-template"]');
            expect(addViewNewButtonShow).toBeTruthy();
            expect(addNewTemplateButton).toBeFalsy();
          });
    });
  });

  it('getTemplateList fetches template list and sets selectedTemplate', () => {
    const templateService = TestBed.get(TemplateService);
    spyOn(templateService, 'list').and.callThrough();
    emailTemplate.getTemplateList();
    fixture.detectChanges();
    templateService.list().subscribe(() => {
      expect(emailTemplate.templates.length).toEqual(2);
      const mockTemplate = new Template({
        name: 'test_email_template_1',
        body: 'hello world',
        title: 'test_title'
      });
      expect(emailTemplate.selectedTemplate.value).toEqual(mockTemplate);
    });
  });

  it('goBack sets showNewView, resets form, and calls GetTemplateList', () => {
    fixture.detectChanges();
    spyOn(emailTemplate.templatesForm, 'reset').and.callThrough();
    spyOn(emailTemplate, 'getTemplateList').and.callThrough();
    emailTemplate.goBack();
    fixture.detectChanges();
    expect(emailTemplate.showNewView).toBe(false);
    expect(emailTemplate.getTemplateList).toHaveBeenCalledTimes(1);
    expect(emailTemplate.templatesForm.reset).toHaveBeenCalledTimes(1);
  });

  describe('goBackToEditView', () => {
    it('param true calls goBack once', () => {
      spyOn(emailTemplate, 'goBack').and.callThrough();
      emailTemplate.goBackToEditView(true);
      fixture.detectChanges();
      expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
    });

    it('confirm Yes returns to Edit View', () => {
      const compiled = fixture.debugElement.nativeElement;
      let addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      spyOn(emailTemplate, 'goBackToEditView').and.callThrough();
      spyOn(emailTemplate, 'goBack').and.callThrough();
      spyOn(dialogService, 'confirm')
          .and.returnValue(of(true))
          .and.callThrough();
      addNewViewButton.click();
      fixture.detectChanges();
      let goBackButton =
          compiled.querySelector('button[name="back-to-edit-template"]');
      addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      expect(goBackButton).toBeTruthy();
      expect(addNewViewButton).toBeFalsy();
      goBackButton.click();
      expect(emailTemplate.goBackToEditView).toHaveBeenCalledTimes(1);
      expect(dialogService.confirm).toHaveBeenCalledTimes(1);
      fixture.detectChanges();
      dialogService.confirm('', '').subscribe(() => {
        expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
        const addViewNewButtonShow =
            compiled.querySelector('button[name="show-new-template-view"]');
        goBackButton =
            compiled.querySelector('button[name="back-to-edit-template"]');
        expect(addViewNewButtonShow).toBeTruthy();
        expect(goBackButton).toBeFalsy();
      });
    });

    it('confirm cancel keeps Add New View', () => {
      const compiled = fixture.debugElement.nativeElement;
      let addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      spyOn(emailTemplate, 'goBackToEditView').and.callThrough();
      spyOn(emailTemplate, 'goBack').and.callThrough();
      spyOn(dialogService, 'confirm')
          .and.returnValue(of(false))
          .and.callThrough();
      addNewViewButton.click();
      fixture.detectChanges();
      let goBackButton =
          compiled.querySelector('button[name="back-to-edit-template"]');
      addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      expect(goBackButton).toBeTruthy();
      expect(addNewViewButton).toBeFalsy();
      goBackButton.click();
      expect(emailTemplate.goBackToEditView).toHaveBeenCalledTimes(1);
      expect(dialogService.confirm).toHaveBeenCalledTimes(1);
      fixture.detectChanges();
      dialogService.confirm('', '').subscribe(() => {
        expect(emailTemplate.goBack).toHaveBeenCalledTimes(0);
        const addViewNewButtonShow =
            compiled.querySelector('button[name="show-new-template-view"]');
        goBackButton =
            compiled.querySelector('button[name="back-to-edit-template"]');
        expect(addViewNewButtonShow).toBeFalsy();
        expect(goBackButton).toBeTruthy();  //
      });
    });

    describe('removeTemplate', () => {
      it('calls TemplateService.remove and calls goBack', () => {
        const templateService = TestBed.get(TemplateService);
        updateForm('testName', 'testBody', 'testTitle');
        spyOn(templateService, 'remove').and.callThrough();
        spyOn(emailTemplate, 'removeTemplate').and.callThrough();
        spyOn(emailTemplate, 'goBack').and.callThrough();
        spyOn(dialogService, 'confirm')
            .and.returnValue(of(true))
            .and.callThrough();
        emailTemplate.removeTemplate();
        fixture.detectChanges();
        expect(dialogService.confirm).toHaveBeenCalledTimes(1);
        dialogService.confirm('', '').subscribe(() => {
          expect(emailTemplate.removeTemplate).toHaveBeenCalledTimes(1);
          expect(templateService.remove).toHaveBeenCalledTimes(1);
          templateService.remove(new Template(emailTemplate.template.value))
              .subscribe(() => {
                expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
              });
        });
      });

      it('button click and confirm Yes stays on Edit View', () => {
        const compiled = fixture.debugElement.nativeElement;
        const templateService = TestBed.get(TemplateService);
        spyOn(templateService, 'remove').and.callThrough();
        spyOn(emailTemplate, 'removeTemplate').and.callThrough();
        spyOn(emailTemplate, 'goBack').and.callThrough();
        spyOn(dialogService, 'confirm')
            .and.returnValue(of(true))
            .and.callThrough();
        let removeButton =
            compiled.querySelector('button[name="remove-template"]');
        let addNewTemplateButton =
            compiled.querySelector('button[name="add-new-template"]');
        expect(removeButton).toBeTruthy();
        expect(addNewTemplateButton).toBeFalsy();
        removeButton.click();
        fixture.detectChanges();
        expect(emailTemplate.removeTemplate).toHaveBeenCalledTimes(1);
        expect(dialogService.confirm).toHaveBeenCalledTimes(1);
        dialogService.confirm('', '').subscribe(() => {
          expect(templateService.remove).toHaveBeenCalledTimes(1);
          templateService.remove(new Template(emailTemplate.template.value))
              .subscribe(() => {
                expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
                removeButton =
                    compiled.querySelector('button[name="remove-template"]');
                addNewTemplateButton =
                    compiled.querySelector('button[name="add-new-template"]');
                expect(removeButton).toBeTruthy();
                expect(addNewTemplateButton).toBeFalsy();
              });
        });
      });

      it('button click and confirm cancel does not remove template', () => {
        const compiled = fixture.debugElement.nativeElement;
        const templateService = TestBed.get(TemplateService);
        spyOn(templateService, 'remove').and.callThrough();
        spyOn(emailTemplate, 'removeTemplate').and.callThrough();
        spyOn(emailTemplate, 'goBack').and.callThrough();
        spyOn(dialogService, 'confirm')
            .and.returnValue(of(false))
            .and.callThrough();
        let removeButton =
            compiled.querySelector('button[name="remove-template"]');
        let addNewTemplateButton =
            compiled.querySelector('button[name="add-new-template"]');
        expect(removeButton).toBeTruthy();
        expect(addNewTemplateButton).toBeFalsy();
        removeButton.click();
        fixture.detectChanges();
        expect(emailTemplate.removeTemplate).toHaveBeenCalledTimes(1);
        expect(dialogService.confirm).toHaveBeenCalledTimes(1);
        dialogService.confirm('', '').subscribe(() => {
          expect(templateService.remove).toHaveBeenCalledTimes(0);
          expect(emailTemplate.goBack).toHaveBeenCalledTimes(1);
          removeButton =
              compiled.querySelector('button[name="remove-template"]');
          addNewTemplateButton =
              compiled.querySelector('button[name="add-new-template"]');
          expect(removeButton).toBeTruthy();
          expect(addNewTemplateButton).toBeFalsy();
        });
      });
    });

    describe('saveTemplate', () => {
      it('saves updated props and calls getTemplateList', () => {
        updateTemplateSelected('testName', 'testBody', 'testTitle');
        updateForm('testName', 'updateBody', 'updateTitle');
        const templateService = TestBed.get(TemplateService);
        spyOn(templateService, 'update').and.callThrough();
        spyOn(emailTemplate, 'getTemplateList').and.callThrough();
        emailTemplate.saveTemplate();
        fixture.detectChanges();
        expect(templateService.update).toHaveBeenCalledTimes(1);
        const updateTemplate = new Template(emailTemplate.template.value);
        templateService.update(updateTemplate).subscribe(() => {
          expect(emailTemplate.getTemplateList).toHaveBeenCalledTimes(1);
          const selectIndex = emailTemplate.templates.findIndex(
              item => item.name === updateTemplate.name);
          expect(emailTemplate.getTemplateList)
              .toHaveBeenCalledWith(selectIndex);
        });
      });

      it('button click saves template and calls getTemplateList', () => {
        const compiled = fixture.debugElement.nativeElement;
        const saveTemplateButton =
            compiled.querySelector('button[name="save-template"]');
        emailTemplate.selectedTemplate.setValue(
            emailTemplate.templates[1], {onlySelf: true});
        const templateBodyInput =
            emailTemplate.templatesForm.get(['template', 'body']);
        const templateBodyTitle =
            emailTemplate.templatesForm.get(['template', 'title']);
        const templateService = TestBed.get(TemplateService);
        spyOn(templateService, 'update').and.callThrough();
        spyOn(emailTemplate, 'getTemplateList').and.callThrough();
        templateBodyInput!.setValue('test body');
        templateBodyTitle!.setValue('test title');
        saveTemplateButton.click();
        fixture.detectChanges();
        expect(templateService.update).toHaveBeenCalledTimes(1);
        templateService.update(emailTemplate.selectedTemplate.value)
            .subscribe(() => {
              expect(emailTemplate.getTemplateList).toHaveBeenCalledTimes(1);
              const selectIndex = emailTemplate.templates.findIndex(
                  item =>
                      item.name === emailTemplate.selectedTemplate.value.name);
              expect(emailTemplate.getTemplateList)
                  .toHaveBeenCalledWith(selectIndex);
            });
      });
    });
  });

  describe('formValidation', () => {
    it('edit view form valid with expect body and title', () => {
      const templateBodyInput =
          emailTemplate.templatesForm.get(['template', 'body']);
      const templateBodyTitle =
          emailTemplate.templatesForm.get(['template', 'title']);
      templateBodyInput!.setValue('');
      templateBodyTitle!.setValue('');
      expect(emailTemplate.templatesForm.valid).toBeTruthy();
    });

    it('add new view form invalid with empty name field', () => {
      const compiled = fixture.debugElement.nativeElement;
      const addNewViewButton =
          compiled.querySelector('button[name="show-new-template-view"]');
      const templateService = TestBed.get(TemplateService);
      spyOn(templateService, 'create').and.callThrough();
      spyOn(emailTemplate, 'addTemplate').and.callThrough();
      spyOn(emailTemplate, 'goBackToEditView').and.callThrough();
      spyOn(emailTemplate, 'goBack').and.callThrough();
      addNewViewButton.click();
      fixture.detectChanges();
      const templateNameInput =
          emailTemplate.templatesForm.get(['template', 'name']);
      const errors = templateNameInput!.errors;
      expect(errors!['required']).toBeTruthy();
      expect(emailTemplate.templatesForm.valid).toBeFalsy();
    });
  });
});
