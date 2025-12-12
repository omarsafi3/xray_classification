import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from  '../../environment/environment.dev';

export interface GlobalMetrics { //faster than a class
  id?: number; // id may be undefined, to be checked
  round: number;
  testLoss: number;
  testAccuracy: number;
  sensitivity: number;
  specificity: number;
  datetime: string;
}

@Injectable({
  providedIn: 'root' //singleton service
})  
export class GlobalMetricsService {
  private apiUrl = environment.apiUrl+'/model';

  constructor(private http: HttpClient) {} //http is both a parameter and a property of the class 

  getAllMetrics(): Observable<GlobalMetrics[]> {
    return this.http.get<GlobalMetrics[]>(`${this.apiUrl}/metrics/all`);
  }

  getLatestMetrics(): Observable<GlobalMetrics> {
    return this.http.get<GlobalMetrics>(`${this.apiUrl}/metrics/latest`);
  }
  
  //this api method will probably never be needed since the python script is the one to the backend:

  // saveMetrics(metrics: GlobalMetrics): Observable<GlobalMetrics> {
  //   return this.http.post<GlobalMetrics>(`${this.apiUrl}/metrics/save`, metrics);
  // }

}
