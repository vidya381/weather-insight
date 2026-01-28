package com.example.temperature_converter.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.ResponseEntity;

@SpringBootTest
class TemperatureConverterControllerTest {

    @Autowired
    private TemperatureConverterController controller;

    @Test
    void testConvertCelsiusToFahrenheit() {
        ResponseEntity<String> response = controller.convert(0, "Celsius", "Fahrenheit");
        assertEquals("0.00 Celsius is 32.00 Fahrenheit", response.getBody());
    }

    @Test
    void testConvertFahrenheitToCelsius() {
        ResponseEntity<String> response = controller.convert(32, "Fahrenheit", "Celsius");
        assertEquals("32.00 Fahrenheit is 0.00 Celsius", response.getBody());
    }

    @Test
    void testConvertCelsiusToKelvin() {
        ResponseEntity<String> response = controller.convert(0, "Celsius", "Kelvin");
        assertEquals("0.00 Celsius is 273.15 Kelvin", response.getBody());
    }

    @Test
    void testConvertKelvinToCelsius() {
        ResponseEntity<String> response = controller.convert(273.15, "Kelvin", "Celsius");
        assertEquals("273.15 Kelvin is 0.00 Celsius", response.getBody());
    }

    @Test
    void testConvertCelsiusToRankine() {
        ResponseEntity<String> response = controller.convert(0, "Celsius", "Rankine");
        assertEquals("0.00 Celsius is 491.67 Rankine", response.getBody());
    }

    @Test
    void testConvertRankineToCelsius() {
        ResponseEntity<String> response = controller.convert(491.67, "Rankine", "Celsius");
        assertEquals("491.67 Rankine is 0.00 Celsius", response.getBody());
    }

    @Test
    void testConvertCelsiusToReaumur() {
        ResponseEntity<String> response = controller.convert(100, "Celsius", "Réaumur");
        assertEquals("100.00 Celsius is 80.00 Réaumur", response.getBody());
    }

    @Test
    void testConvertReaumurToCelsius() {
        ResponseEntity<String> response = controller.convert(80, "Réaumur", "Celsius");
        assertEquals("80.00 Réaumur is 100.00 Celsius", response.getBody());
    }

    @Test
    void testConvertBetweenNonCelsiusScales() {
        ResponseEntity<String> response = controller.convert(32, "Fahrenheit", "Kelvin");
        assertEquals("32.00 Fahrenheit is 273.15 Kelvin", response.getBody());
    }

    @Test
    void testInvalidFromScale() {
        ResponseEntity<String> response = controller.convert(0, "InvalidScale", "Celsius");
        assertEquals(400, response.getStatusCodeValue());
        assertEquals("Unsupported scale: InvalidScale", response.getBody());
    }

    @Test
    void testInvalidToScale() {
        ResponseEntity<String> response = controller.convert(0, "Celsius", "InvalidScale");
        assertEquals(400, response.getStatusCodeValue());
        assertEquals("Unsupported scale: InvalidScale", response.getBody());
    }
}