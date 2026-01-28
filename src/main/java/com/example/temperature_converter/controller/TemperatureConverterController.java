package com.example.temperature_converter.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/convert")
public class TemperatureConverterController {

    @GetMapping
    public ResponseEntity<String> convert(@RequestParam double temperature, 
                                          @RequestParam String fromScale, 
                                          @RequestParam String toScale) {
        try {
            double convertedTemp = convertTemperature(temperature, fromScale, toScale);
            String result = String.format("%.2f %s is %.2f %s", temperature, fromScale, convertedTemp, toScale);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    private double convertTemperature(double temp, String fromScale, String toScale) {
        // Convert to Celsius first
        double celsius;
        switch (fromScale.toLowerCase()) {
            case "celsius": celsius = temp; break;
            case "fahrenheit": celsius = (temp - 32) * 5 / 9; break;
            case "kelvin": celsius = temp - 273.15; break;
            case "rankine": celsius = (temp - 491.67) * 5 / 9; break;
            case "réaumur": celsius = temp * 5 / 4; break;
            default: throw new IllegalArgumentException("Unsupported scale: " + fromScale);
        }

        // Convert from Celsius to target scale
        switch (toScale.toLowerCase()) {
            case "celsius": return celsius;
            case "fahrenheit": return celsius * 9 / 5 + 32;
            case "kelvin": return celsius + 273.15;
            case "rankine": return (celsius + 273.15) * 9 / 5;
            case "réaumur": return celsius * 4 / 5;
            default: throw new IllegalArgumentException("Unsupported scale: " + toScale);
        }
    }
}