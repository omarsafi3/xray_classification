import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component } from '@angular/core';
import { environment } from '../../environment/environment.dev';

@Component({
  selector: 'app-download',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fl-client.html',
  styleUrls: ['./fl-client.scss']
})
export class FlClientComponent {
  constructor(private http: HttpClient) {}

  downloadClient() {
   const token = localStorage.getItem('access_token'); 

  if (!token) {
    alert('Please login to download the client.');
    return;
  }

  const headers = new HttpHeaders({
    'Authorization': `Bearer ${token}`
  });

  this.http.get(`${environment.apiUrl}/download/client-zip`, {
    headers,
    responseType: 'blob' 
  }).subscribe(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'client.zip';
    a.click();
    window.URL.revokeObjectURL(url);
  }, error => {
    console.error('Download failed', error);
    alert('Download failed. Make sure you are logged in.');
  });
}
}