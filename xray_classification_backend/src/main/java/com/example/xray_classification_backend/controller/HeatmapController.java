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

            // Full absolute path to your Python script
            String pythonScriptPath = "C:\\Users\\safio\\Desktop\\xray_classification\\python\\heatmap.py";

            ProcessBuilder builder = new ProcessBuilder(
                    "C:\\Users\\safio\\.conda\\envs\\tf211\\python.exe",
                    pythonScriptPath,
                    "--img_path", tempImage.getAbsolutePath()
            );

            builder.redirectErrorStream(true);
            Process process = builder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder logs = new StringBuilder();  // to collect all logs
            String jsonLine = null;                    // to store the JSON line output

            while ((line = reader.readLine()) != null) {
                System.out.println("[PYTHON] " + line);  // log for debugging

                // Check if line looks like JSON (starts with '{')
                if (line.trim().startsWith("{")) {
                    jsonLine = line.trim();
                } else {
                    logs.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            System.out.println("Python script exited with code: " + exitCode);

            if (exitCode != 0) {
                return ResponseEntity.status(500)
                        .body(Map.of("error", "Python script failed", "details", logs.toString()));
            }

            if (jsonLine == null) {
                // No JSON output found in script
                return ResponseEntity.status(500)
                        .body(Map.of("error", "No JSON output from Python script", "logs", logs.toString()));
            }

            // Parse JSON output from Python script
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> result = mapper.readValue(jsonLine, Map.class);

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Internal server error"));
        }

    }
}
