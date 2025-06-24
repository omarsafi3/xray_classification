package com.example.xray_classification_backend.repository;

import com.example.xray_classification_backend.model.GlobalMetrics;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GlobalMetricsInterface extends JpaRepository<GlobalMetrics, Integer> {
}
