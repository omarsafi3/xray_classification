package com.example.xray_classification_backend.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "global_metrics")
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class GlobalMetrics {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private int id;
    private int round;
    private double testLoss;
    private double testAccuracy;
    private double sensitivity;
    private double specificity;
    @Column(name="date_time")
    private LocalDateTime dateTime;

}
