package com.example.xray_classification_backend.controller;

import com.example.xray_classification_backend.model.HeatmapEntity;
import com.example.xray_classification_backend.repository.HeatmapRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/v1/heatmap")
public class HeatmapController {

    @Autowired
    private HeatmapRepository heatmapRepository;

    @PostMapping("/upload")
    public ResponseEntity<String> uploadHeatmap(
            @RequestParam("file") MultipartFile file,
            @RequestParam("prediction") String prediction) {
        try {
            HeatmapEntity heatmap = new HeatmapEntity();
            heatmap.setImage(file.getBytes());
            heatmap.setPrediction(prediction);
            heatmapRepository.save(heatmap);

            return ResponseEntity.ok("Saved successfully with prediction: " + prediction);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to save image.");
        }
    }
}
