package com.example.temperature_converter;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class TemperatureConverterIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testConvertCelsiusToFahrenheit() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "0")
                .param("fromScale", "Celsius")
                .param("toScale", "Fahrenheit"))
                .andExpect(status().isOk())
                .andExpect(content().string("0.00 Celsius is 32.00 Fahrenheit"));
    }

    @Test
    public void testConvertFahrenheitToCelsius() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "32")
                .param("fromScale", "Fahrenheit")
                .param("toScale", "Celsius"))
                .andExpect(status().isOk())
                .andExpect(content().string("32.00 Fahrenheit is 0.00 Celsius"));
    }

    @Test
    public void testConvertCelsiusToKelvin() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "0")
                .param("fromScale", "Celsius")
                .param("toScale", "Kelvin"))
                .andExpect(status().isOk())
                .andExpect(content().string("0.00 Celsius is 273.15 Kelvin"));
    }

    @Test
    public void testConvertKelvinToRankine() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "0")
                .param("fromScale", "Kelvin")
                .param("toScale", "Rankine"))
                .andExpect(status().isOk())
                .andExpect(content().string("0.00 Kelvin is 0.00 Rankine"));
    }

    @Test
    public void testConvertReaumurToFahrenheit() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "80")
                .param("fromScale", "Réaumur")
                .param("toScale", "Fahrenheit"))
                .andExpect(status().isOk())
                .andExpect(content().string("80.00 Réaumur is 212.00 Fahrenheit"));
    }

    @Test
    public void testInvalidScale() throws Exception {
        mockMvc.perform(get("/api/convert")
                .param("temperature", "0")
                .param("fromScale", "InvalidScale")
                .param("toScale", "Celsius"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string("Unsupported scale: InvalidScale"));
    }
}