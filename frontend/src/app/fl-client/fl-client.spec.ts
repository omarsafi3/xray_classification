import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FlClient } from './fl-client';

describe('FlClient', () => {
  let component: FlClient;
  let fixture: ComponentFixture<FlClient>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FlClient]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FlClient);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
