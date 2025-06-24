package com.example.xray_classification_backend.service;

import com.example.xray_classification_backend.model.GlobalMetrics;
import java.util.List;

import com.example.xray_classification_backend.repository.GlobalMetricsInterface;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
@Service
public class GlobalMetricsService {


    @Autowired
    private GlobalMetricsInterface globalMetricsInterface;

    public List<GlobalMetrics> getAllGlobalMetrics() {
        return globalMetricsInterface.findAll();
    }

    public GlobalMetrics getGlobalMetricsById(int id) {
        return globalMetricsInterface.findById(id).orElse(null);
    }

    public GlobalMetrics saveGlobalMetrics(GlobalMetrics globalMetrics) {
        return globalMetricsInterface.save(globalMetrics);
    }

    public void deleteGlobalMetrics(int id) {
        globalMetricsInterface.deleteById(id);
    }


}
