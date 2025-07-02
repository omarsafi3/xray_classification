package com.example.xray_classification_backend.controller;

import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;

@RestController
@RequestMapping("/api/v1/download")
public class DownloadController {

    @GetMapping("/client-zip")
    public ResponseEntity<Resource> downloadClientZip() throws IOException {
        // Load the ZIP from resources (classpath)
        Resource resource = new ClassPathResource("static/download/client_bundle.zip");

        if (!resource.exists()) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"client_bundle.zip\"")
                .body(resource);
    }
}
