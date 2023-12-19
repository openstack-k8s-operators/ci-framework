package main

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v2"
)

type ConfigEntry struct {
    Name string `yaml:"name"`
    Release string `yaml:"release"`
    Job string `yaml:"job_name"`
    Api string `yaml:"api_entry"`
    FromNamespace string `yaml:"from_namespace"`
    ToNamespace string `yaml:"to_namespace"`
}

type Config struct {
    ZuulAPI string `yaml:"zuul_api"`
    PullRegistry string `yaml:"pull_registry"`
    PushRegistry string `yaml:"push_registry"`
    Entries []ConfigEntry `yaml:"entries"`
}

func NewConfig(configPath string) (*Config, error) {
    config := &Config{}

    file, err := os.Open(configPath)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    d := yaml.NewDecoder(file)

    if err := d.Decode(&config); err != nil {
        return nil, err
    }
    return config, nil
}

func ValidateConfigPath(path string) error {
    s, err := os.Stat(path)
    if err != nil {
        return err
    }
    if s.IsDir() {
        return fmt.Errorf("'%s' is a directory, not a normal file", path)
    }
    return nil
}
