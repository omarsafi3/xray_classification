import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { environment } from '../../environment/environment.dev';
import { UploadService } from '../services/upload.service';


@Component({
  selector: 'app-upload-image',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload-image.html',
  styleUrls: ['./upload-image.scss']
})

export class UploadImageComponent {

  prediction: string = '';
  heatmapImage: string = '';
  message: string = '';
  uploadedImageUrl: string | null = null;
  loadingHeatmap: boolean = false; 


  constructor(private uploadService: UploadService){}

  onFileSelected(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length === 1) {
        this.uploadService.selectedFile = fileInput.files[0];
        }
    }

  uploadImage() {
  if (!this.uploadService.selectedFile) {
    alert('Please select a file.');
    return;
  }

  this.loadingHeatmap = true;  

  this.uploadedImageUrl = URL.createObjectURL(this.uploadService.selectedFile);

  this.uploadService.uploadImage().subscribe({
    next: (response) => {
      this.prediction = response.prediction;
      this.heatmapImage = 'data:image/png;base64,' + response.heatmap_base64;
      this.message = 'Prediction complete.';
      this.loadingHeatmap = false;
    },
    error: (err) => {
      console.error('Upload failed:', err);
      this.message = 'Upload failed.';
      this.loadingHeatmap = false;
    }
  });
}

}

  
