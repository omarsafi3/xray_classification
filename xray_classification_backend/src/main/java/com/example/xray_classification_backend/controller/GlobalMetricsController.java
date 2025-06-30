package com.example.xray_classification_backend.controller;

import com.example.xray_classification_backend.model.GlobalMetrics;
import com.example.xray_classification_backend.service.GlobalMetricsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/v1/model/metrics")
public class GlobalMetricsController {

    @Autowired
    private GlobalMetricsService globalMetricsService;

    @GetMapping("/all")
    public List<GlobalMetrics> getGlobalMetrics() {
        List<GlobalMetrics> globalMetricsList = globalMetricsService.getAllGlobalMetrics();
        if (globalMetricsList.isEmpty()) {
            return List.of(new GlobalMetrics(0, 0, 0, 0, 0, 0, LocalDateTime.now()));
        }
        return globalMetricsList;

    }

    @PostMapping("/save")
    public GlobalMetrics saveGlobalMetrics(@RequestBody GlobalMetrics globalMetrics) {
        return globalMetricsService.saveGlobalMetrics(globalMetrics);
    }

    @GetMapping("/latest") public GlobalMetrics getLatestGlobalMetrics() {
        List<GlobalMetrics> globalMetricsList = globalMetricsService.getAllGlobalMetrics();
        if (globalMetricsList.isEmpty()) {
            return new GlobalMetrics(0, 0, 0, 0, 0, 0, LocalDateTime.now());
        }
        return globalMetricsList.get(globalMetricsList.size() - 1);
    }

}
