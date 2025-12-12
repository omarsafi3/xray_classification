import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { GlobalMetrics, GlobalMetricsService } from '../services/global-metrics';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { NgChartsModule } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';



@Component({
  selector: 'app-global-metrics-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatPaginatorModule, NgChartsModule],
  templateUrl: './global-metrics-list.html',
  styleUrls: ['./global-metrics-list.scss'] 
})
export class GlobalMetricsList implements OnInit, AfterViewInit {
  displayedColumns: string[] = ['round', 'testLoss', 'testAccuracy', 'sensitivity', 'specificity', 'dateTime'];
  dataSource = new MatTableDataSource<GlobalMetrics>([]);
  latestMetrics?: GlobalMetrics;
  // Chart-related properties
chartData: ChartConfiguration<'line'>['data'] = {
  labels: [],
  datasets: [
    {
      data: [],
      label: 'Test Accuracy (%)',
      fill: false,
      borderColor: '#007bff',
      tension: 0.3,
    }
  ]
};

chartOptions: ChartConfiguration<'line'>['options'] = {
  responsive: true,
  plugins: {
    legend: {
      display: true
    }
  },
  scales: {
    x: {},
    y: {
      min: 0,
      max: 100
    }
  }
};

  @ViewChild(MatPaginator, { static: false }) paginator!: MatPaginator;

  constructor(private globalMetricsService: GlobalMetricsService) {}

  ngOnInit(): void {


    this.globalMetricsService.getAllMetrics().subscribe((d: GlobalMetrics[]) => {
  this.dataSource.data = d;

  this.chartData = {
    labels: d.map(m => `Round ${m.round}`),
    datasets: [
      {
        data: d.map(m => parseFloat((m.testAccuracy * 100).toFixed(2))),
        label: 'Test Accuracy (%)',
        fill: false,
        borderColor: '#007bff',
        tension: 0.3,
      }
    ]
  };
});


    this.globalMetricsService.getLatestMetrics().subscribe((l: GlobalMetrics)=> {
      this.latestMetrics = l;
    });
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
  }
}
