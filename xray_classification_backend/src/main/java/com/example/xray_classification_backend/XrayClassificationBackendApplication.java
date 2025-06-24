package com.example.xray_classification_backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;


@SpringBootApplication
public class XrayClassificationBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(XrayClassificationBackendApplication.class, args);
    }

}
