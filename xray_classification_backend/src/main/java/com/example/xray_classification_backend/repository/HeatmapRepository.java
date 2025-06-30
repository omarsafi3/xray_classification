package com.example.xray_classification_backend.repository;

import com.example.xray_classification_backend.model.HeatmapEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface HeatmapRepository extends JpaRepository<HeatmapEntity, Long> {}
