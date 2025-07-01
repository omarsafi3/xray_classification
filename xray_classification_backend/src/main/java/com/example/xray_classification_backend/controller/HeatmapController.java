package com.example.xray_classification_backend.controller;

import com.example.xray_classification_backend.model.HeatmapEntity;
import com.example.xray_classification_backend.repository.HeatmapRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Map;

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
    @PostMapping("/predict")
    public ResponseEntity<Map<String, Object>> predict(@RequestParam("file") MultipartFile file) {
        try {
            // Save uploaded file to a temporary location
            String tempDir = System.getProperty("java.io.tmpdir");
            File tempImage = new File(tempDir, file.getOriginalFilename());
            file.transferTo(tempImage);

            // Run the Python script and pass the image path
            ProcessBuilder builder = new ProcessBuilder(
                    "C:\\Users\\safio\\anaconda3\\envs\\tf211\\python.exe",
                    "heatmap.py",
                    "--img_path", tempImage.getAbsolutePath()
            );

            builder.redirectErrorStream(true);
            Process process = builder.start();

            // Read the script output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                return ResponseEntity.status(500).body(Map.of("error", "Python script failed"));
            }

            // Parse JSON output from Python (you'll format the output there)
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> result = mapper.readValue(output.toString(), Map.class);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Internal server error"));
        }
    }

}
