import { Injectable } from "@angular/core";
import { environment } from "../../environment/environment.dev";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: 'root'
})

export class UploadService {
    private apiUrl = environment.apiUrl;
    selectedFile: File | null = null;
    message: string = ''; 
    heatmapImage: string | null = null;
    prediction: string = '';
    constructor(private http: HttpClient){}

   uploadImage(): Observable<HeatmapResponse> {
  const formData = new FormData();
  formData.append('file', this.selectedFile!); // safe because null is checked before calling
  return this.http.post<HeatmapResponse>(`${this.apiUrl}/heatmap/predict`, formData);
}



  }
