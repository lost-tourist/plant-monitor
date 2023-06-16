# plant-monitor

## Introduction

This makes use of a Raspbery Pi Pico W and a [Monk Makes plant monitor](https://monkmakes.com/pmon.html) to
keep an eye on the status of a plant being grown. My use-case is a tomato plant that I am growing in a greenhouse
in my garden.

## Concept

The plant monitor hardware will provide readings for air temperature, air humidity and soil moisture values
on demand. The Pico polls the plant monitor periodically (every 5 minutes by default) and then sends the readings
via HTTP to a REST API running on a server somewhere.

This architecture is designed to minimise the power usage of the Pico W as it is running from batteries.

The data received by the REST endpoint is written to a basic CSV file from where it can be analysed, plotted, etc.
