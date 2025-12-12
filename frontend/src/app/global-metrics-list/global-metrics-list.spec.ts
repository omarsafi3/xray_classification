import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GlobalMetricsList } from './global-metrics-list';

describe('GlobalMetricsList', () => {
  let component: GlobalMetricsList;
  let fixture: ComponentFixture<GlobalMetricsList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GlobalMetricsList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GlobalMetricsList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
